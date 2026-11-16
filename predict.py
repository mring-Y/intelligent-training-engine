"""Independent stdin/stdout JSONL model entry; training is never invoked."""

from ite.continuation import prediction_main


if __name__ == "__main__":
    raise SystemExit(prediction_main())
