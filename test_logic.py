from src import analyze_stock
import json

def test_ticker(symbol):
    print(f"Testing {symbol}...")
    result = analyze_stock(symbol)
    if result:
        print(f"SUCCESS: {symbol}")
        print(f"Score: {result['score']['total']} ({result['score']['rating']})")
        print(f"Price: {result['data']['price']}")
        print(f"Fair Value: {result['valuations']['combined']}")
    else:
        print(f"FAILED: {symbol}")

if __name__ == "__main__":
    test_ticker("AAPL")
    test_ticker("INVALID123")
