#!/usr/bin/env python3
"""
Batch scraper with:
- Resume from checkpoint (checkpoint.json)
- Dedup by URL
- Retry failed items
- Progress report
"""
import json
import asyncio
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from orchestrator import process_bookmark, TODAY


async def batch_scrape(bookmarks, batch_size=10, delay=2):
    """Batch scrape with checkpoint, dedup, and progress."""
    # Dedup by URL
    seen_urls = set()
    unique = []
    for bm in bookmarks:
        url = bm.get('url', '')
        if url not in seen_urls:
            seen_urls.add(url)
            unique.append(bm)
    print(f'📋 Deduplicated: {len(bookmarks)} → {len(unique)}')

    # Load checkpoint (already processed URLs)
    checkpoint_file = Path('/tmp/scrape_checkpoint.json')
    processed = set()
    if checkpoint_file.exists():
        with open(checkpoint_file, 'r') as f:
            data = json.load(f)
            processed = set(data.get('urls', []))
        print(f'📂 Checkpoint: {len(processed)} already processed')

    # Filter out already processed
    to_process = [bm for bm in unique if bm.get('url', '') not in processed]
    print(f'🔄 To process: {len(to_process)}')

    if not to_process:
        print('✅ All bookmarks already processed!')
        return {'total': len(unique), 'processed': len(unique), 'success': 0, 'failed': 0}

    results = []
    success_count = 0
    fail_count = 0
    start_time = time.time()

    for i, bm in enumerate(to_process, 1):
        url = bm.get('url', '')
        print(f'[{i}/{len(to_process)}] {bm.get("title", url[:40])[:50]}')

        try:
            result_dict = await process_bookmark(bm, i, len(to_process))
            results.append(result_dict)

            if result_dict['success']:
                success_count += 1
            else:
                fail_count += 1

        except Exception as e:
            print(f'  ❌ Exception: {e}')
            fail_count += 1
            results.append({
                'title': bm.get('title', ''),
                'url': url,
                'folder': bm.get('folder', '其他'),
                'strategy': 'unknown',
                'success': False,
                'content_length': 0,
                'saved_path': '',
                'quality': 'exception',
            })

        # Rate limiting
        if i % batch_size == 0 and i < len(to_process):
            print(f'  ⏳ Waiting {delay}s...')
            await asyncio.sleep(delay)

        # Save checkpoint every 5 items
        if i % 5 == 0:
            processed.update([bm.get('url', '') for bm in to_process[:i]])
            with open(checkpoint_file, 'w') as f:
                json.dump({'urls': list(processed)}, f, ensure_ascii=False)

    elapsed = time.time() - start_time
    rate = len(to_process) / elapsed if elapsed > 0 else 0

    # Save summary
    summary = {
        'total': len(to_process),
        'success': success_count,
        'failed': fail_count,
        'elapsed_seconds': round(elapsed, 1),
        'rate_per_minute': round(rate * 60, 1),
        'results': results,
    }
    with open('/tmp/scrape_batch_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f'\n{"="*60}')
    print(f'📊 BATCH COMPLETE')
    print(f'  Processed: {success_count + fail_count}')
    print(f'  ✅ Success: {success_count}')
    print(f'  ❌ Failed: {fail_count}')
    print(f'  ⏱ Time: {elapsed:.1f}s ({rate:.1f} req/s)')
    print(f'{"="*60}')

    return summary


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Batch hybrid scraper')
    parser.add_argument('--input', required=True, help='Input JSON bookmarks file')
    parser.add_argument('--batch-size', type=int, default=10, help='Batch size (default: 10)')
    parser.add_argument('--delay', type=float, default=2.0, help='Delay between batches (seconds)')
    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        bookmarks = json.load(f)

    asyncio.run(batch_scrape(bookmarks, args.batch_size, args.delay))
