from django.http import HttpResponse


def home(request):
    return HttpResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>BF Travel</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        h1 {
            font-size: 4rem;
            font-weight: 300;
        }
    </style>
</head>
<body>
    <h1>Hello World</h1>
</body>
</html>
""")
