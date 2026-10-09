#!/usr/bin/env python3
"""Optional local dev server. Binds ONLY to 127.0.0.1 and makes no external requests."""
import argparse
import functools
import http.server
import pathlib
import sys
import webbrowser


def main():
    ap=argparse.ArgumentParser(description='MinimalAdam Studio local editor')
    ap.add_argument('--port',type=int,default=8765)
    ap.add_argument('--no-browser',action='store_true')
    args=ap.parse_args()
    here=pathlib.Path(__file__).resolve().parent
    root=here.parent
    editor=root/'editor'
    if not editor.is_dir():
        print('HATA: editor dizini bulunamadı',file=sys.stderr);return 1
    handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(editor))
    try:
        server=http.server.ThreadingHTTPServer(('127.0.0.1',args.port),handler)
    except OSError as e:
        print(f'HATA: Yerel port açılamadı: {e}',file=sys.stderr);return 1
    url=f'http://127.0.0.1:{server.server_port}/'
    print('MinimalAdam Studio yerel adres:',url,flush=True)
    print('Kapatmak için Ctrl+C. İnternet/API gerektirmez.',flush=True)
    if not args.no_browser:webbrowser.open(url)
    try:server.serve_forever()
    except KeyboardInterrupt:print('\nKapatılıyor...')
    finally:server.server_close()
    return 0

if __name__=='__main__':raise SystemExit(main())
