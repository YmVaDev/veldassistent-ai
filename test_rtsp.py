import cv2

PASSWORD = "YmkeV6581**!"

urls = [
    f"rtsp://admin:{PASSWORD}@192.168.129.66:554/Preview_01_main",
    f"rtsp://admin:{PASSWORD}@192.168.129.66:554/Preview_01_sub",
]

for url in urls:
    print(f"\nTest: {url.replace(PASSWORD, '******')}")

    cap = cv2.VideoCapture(url)

    if not cap.isOpened():
        print("❌ Geen verbinding")
        cap.release()
        continue

    print("✅ RTSP verbinding!")

    success, frame = cap.read()

    if success:
        print(f"✅ Frame ontvangen: {frame.shape}")

        cv2.imwrite("rtsp_test.jpg", frame)
        print("✅ Opgeslagen als rtsp_test.jpg")

        cap.release()
        break
    else:
        print("❌ Verbonden, maar geen frame ontvangen")

    cap.release()