import requests

def test():
    try:
        res = requests.get("http://127.0.0.1:8000/api/trends/youtube?zip_code=800001")
        print("Status Code:", res.status_code)
        data = res.json()
        print("Data Type:", type(data))
        print("Keys:", data.keys())
        print("Data preview:", str(data)[:300])
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test()
