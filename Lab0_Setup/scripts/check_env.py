import sys

def main():
    print(f"Python:        {sys.version.split()[0]}")
    try:
        import torch
        print(f"Torch:         {torch.__version__}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"GPU:           {torch.cuda.get_device_name(0)}")
    except ImportError:
        print("Torch:         NOT INSTALLED")

    try:
        import ultralytics
        from ultralytics import YOLO
        print(f"Ultralytics:   {ultralytics.__version__}  YOLO OK")
    except ImportError:
        print("Ultralytics:   NOT INSTALLED")

if __name__ == "__main__":
    main()
