import streamlit as st
from rembg import remove
from PIL import Image, ImageDraw, ImageFont
import io

def add_text_to_image(image, text, position=None, font_size=50, text_color=(255, 255, 255, 255)):
    """Add text to an image with enhanced styling"""
    text_overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(text_overlay)

    # Try to load a system font, fall back to default if none available
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/Impact.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttf", font_size)
            except:
                font = ImageFont.load_default()
                st.warning("Using default font as system fonts are not accessible")

    # Split text into lines
    lines = text.split('\n')

    # Calculate total height of all lines
    line_spacing = font_size * 0.2
    total_height = (font_size + line_spacing) * len(lines) - line_spacing

    # Calculate starting Y position
    current_y = (image.size[1] - total_height) // 2 if position is None else position[1]

    # Draw each line
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x_position = (image.size[0] - text_width) // 2

        # Draw shadow
        shadow_offset = 3
        draw.text((x_position + shadow_offset, current_y + shadow_offset),
                  line, font=font, fill=(0, 0, 0, 180))

        # Draw main text
        draw.text((x_position, current_y),
                  line, font=font, fill=text_color)

        current_y += font_size + line_spacing

    return text_overlay


def create_layered_image(original_image, text, removed_bg_image, font_size):
    """Create image with three layers: original image, text, and PNG overlay"""
    if original_image.mode != 'RGBA':
        original_image = original_image.convert('RGBA')
    if removed_bg_image.mode != 'RGBA':
        removed_bg_image = removed_bg_image.convert('RGBA')

    text_overlay = add_text_to_image(
        original_image,
        text,
        font_size=font_size
    )

    if removed_bg_image.size != original_image.size:
        removed_bg_image = removed_bg_image.resize(original_image.size, Image.LANCZOS)

    result = Image.alpha_composite(original_image, text_overlay)
    final_result = Image.alpha_composite(result, removed_bg_image)

    return final_result


def main():
    st.title("Text Overlay App")
    st.write("Upload an image and add custom text overlay")

    # File uploader
    uploaded_file = st.file_uploader("Choose an image...", type=['png', 'jpg', 'jpeg'])

    # Text input
    custom_text = st.text_area("Enter text for overlay (use \\n for new line)", "PARTIAL\nWORLD")

    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert('RGBA')

        st.subheader("Original Image")
        st.image(image, use_container_width=True)  # Updated here

        # Slider for font size adjustment
        font_size = st.slider("Font Size", min_value=10, max_value=500, value=int(image.size[1] * 0.15))

        if st.button("Process Image"):
            with st.spinner("Processing..."):
                try:
                    removed_bg = remove(image)
                    final_image = create_layered_image(image, custom_text, removed_bg, font_size)

                    st.subheader("Processed Image")
                    st.image(final_image, use_container_width=True)  # Updated here

                    # Download button
                    buf = io.BytesIO()
                    final_image.save(buf, format='PNG')
                    btn = st.download_button(
                        label="Download Processed Image",
                        data=buf.getvalue(),
                        file_name="processed_image.png",
                        mime="image/png"
                    )
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
