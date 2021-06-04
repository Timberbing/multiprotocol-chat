# Modifying daemon library source code

Run: `vim /usr/local/lib/python3.8/dist-packages/daemon/runner.py`
Modify the following lines (#118):

```python
self.daemon_context = DaemonContext()
self.daemon_context.stdin = open(app.stdin_path, 'wb+',buffering=0)
self.daemon_context.stdout = open(app.stdout_path,  'wb+',buffering=0)
self.daemon_context.stderr = open(
        app.stderr_path, 'wb+', buffering=0)
```

