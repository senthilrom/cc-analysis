from PIL import Image

input_path = r"C:\Users\user\Downloads\geWgxp-y.jpg"        # Replace with your file
output_path = r"C:\Users\user\PycharmProjects\cc-analysis\app.ico"              # Final icon name

img = Image.open(input_path)
img.save(output_path, format='ICO', sizes=[(256, 256)])
print("✅ app.ico generated!")
