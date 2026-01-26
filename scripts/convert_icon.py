from PIL import Image
import os

def convert_ico_to_icns(ico_path, icns_path):
    try:
        if not os.path.exists(ico_path):
            print(f"Error: {ico_path} not found.")
            return

        img = Image.open(ico_path)
        print(f"Opened {ico_path}. Format: {img.format}, Size: {img.size}")
        
        # ICNS format generally expects typical icon sizes. 
        # Pillow's save(..., format='ICNS') usually handles scaling if saving from a large source.
        # But if the ICO contains multiple sizes, we should pick the largest one.
        
        # Check if it's an ICO with multiple sizes
        largest_img = img
        max_size = 0
        
        # Attempt to find the largest frame in the ICO
        try:
            i = 0
            while True:
                img.seek(i)
                w, h = img.size
                if w * h > max_size:
                    max_size = w * h
                    largest_img = img.copy()
                i += 1
        except EOFError:
            pass
            
        print(f"Largest size found: {largest_img.size}")
        
        # Ensure RGBA
        if largest_img.mode != 'RGBA':
            largest_img = largest_img.convert('RGBA')
            
        # Save as ICNS
        largest_img.save(icns_path, format='ICNS')
        print(f"Successfully saved {icns_path}")
        
    except Exception as e:
        print(f"Failed to convert: {e}")

if __name__ == "__main__":
    convert_ico_to_icns("book.ico", "book.icns")
