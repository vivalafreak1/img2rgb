import matplotlib.pyplot as plt
from pandas import DataFrame
from PIL import Image
import streamlit as st

st.set_page_config("img2rgb", "🌈")

st.title("🌈 Image to RGB")

uploaded_image = st.file_uploader("Upload an image", ["jpg", "jpeg", "png", "webp"])

def rgb_to_hsl(rgb):
    r, g, b = [x / 255.0 for x in rgb]
    cmax = max(r, g, b)
    cmin = min(r, g, b)
    delta = cmax - cmin
    
    # Calculate hue
    if delta == 0:
        h = 0
    elif cmax == r:
        h = 60 * (((g - b) / delta) % 6)
    elif cmax == g:
        h = 60 * (((b - r) / delta) + 2)
    else:
        h = 60 * (((r - g) / delta) + 4)
    
    # Calculate lightness
    l = (cmax + cmin) / 2
    
    # Calculate saturation
    if delta == 0:
        s = 0
    else:
        s = delta / (1 - abs(2 * l - 1))
    
    # Scale values to 0-255 range
    h = int(round(h / 360 * 255))
    s = int(round(s * 255))
    l = int(round(l * 255))
    
    return h, s, l

if uploaded_image is not None:
    _, centered_column, _ = st.columns(3)
    centered_column.image(uploaded_image, width=200)

    # Get RGB values and coordinates from user input
    x = st.slider("X Coordinate", 0, 255, 0)
    y = st.slider("Y Coordinate", 0, 255, 0)
    r = st.slider("Red", 0, 255, 0)
    g = st.slider("Green", 0, 255, 0)
    b = st.slider("Blue", 0, 255, 0)
    
    image = Image.open(uploaded_image).convert("RGB")

    image_attrs = {
        "Filename": uploaded_image.name,
        "Type": uploaded_image.type,
        "Mode": image.mode,
        "Resolution": f"{image.width} × {image.height}",
    }

    custom_css = """
        <style>
            thead {
                display: none;
            }
        </style>
    """

    # Display the custom CSS and the table
    st.markdown(custom_css, unsafe_allow_html=True)

    st.table(image_attrs)

    with st.spinner("Getting RGB and HSL values for each pixel..."):
        pixels = list(image.getdata())
        pixel_rgbs = [
            [image.getpixel((x, y)) for x in range(image.width)]
            for y in range(image.height)
        ]
        pixel_hsls = [
            [rgb_to_hsl(image.getpixel((x, y))) for x in range(image.width)]
            for y in range(image.height)
        ]
    
    with st.spinner("Converting pixel data to DataFrame..."):
        df = DataFrame(pixel_rgbs)
        df.index += 1
        df.columns += 1
        df.index.name = "Px"

    with st.spinner("Displaying pixel data..."):
        st.subheader("RGB Pixel Data")
        st.dataframe(df)
        st.caption("Note: Each cell represents the RGB value of a pixel in the image.")

    st.divider()

    with st.spinner("Displaying HSL value.."):
        df_hsl = DataFrame(pixel_hsls)
        df_hsl.index == 1
        df_hsl.columns += 1
        df_hsl.index.name = "Px"

    with st.spinner("Displaying pixel data..."):
        st.subheader("HSL Pixel Data")
        st.dataframe(df_hsl)
        st.caption("Note: Each cell represents the HSL value of a pixel in the image.")    

    n_channels = 4
    n_colors = 256

    with st.spinner("Calculating pixel frequency..."):
        px_freq = [[0 for _ in range(n_colors)] for _ in range(n_channels)]
        for y in pixel_rgbs:
            for rgb in y:
                for c in range(3):
                    px_freq[c][rgb[c]] += 1
                grayscale = round(sum(rgb) / 3)
                px_freq[3][grayscale] += 1

    with st.spinner("Displaying pixel frequency data..."):
        df = DataFrame(px_freq, index=["R", "G", "B", "GS"])
        st.subheader("Pixel Frequency Data")
        st.dataframe(df)

    labels = ["Red", "Green", "Blue", "Gray"]

    with st.spinner("Creating RGB and Grayscale histograms..."):
        fig, ax = plt.subplots(2, 2, figsize=(10, 8))
        for c in range(n_channels):
            row, col = divmod(c, 2)
            ax[row, col].bar(
                range(n_colors), px_freq[c], label=labels[c], color=labels[c]
            )
            ax[row, col].set_title(labels[c])
            ax[row, col].set_xlabel("Pixel Intensity")
        plt.suptitle("RGB Grayscale Histograms")
        plt.tight_layout()

        st.subheader("RGB Grayscale Histograms")
        st.pyplot(fig)

    st.divider()

    with st.spinner("Normalizing histograms..."):
        total_pixels = image.width * image.height
        for i in range(n_channels):
            for j in range(n_colors):
                px_freq[i][j] /= total_pixels

    with st.spinner("Displaying normalized pixel frequency data..."):
        df = DataFrame(px_freq, index=["R", "G", "B", "GS"])
        st.subheader("Normalized Pixel Frequency Data")
        st.dataframe(df)

    with st.spinner("Creating normalized RGB and Grayscale histograms..."):
        fig, ax = plt.subplots(2, 2, figsize=(10, 8))
        for c in range(n_channels):
            row, col = divmod(c, 2)
            ax[row, col].bar(
                range(n_colors), px_freq[c], label=labels[c], color=labels[c]
            )
            ax[row, col].set_title(labels[c])
            ax[row, col].set_xlabel("Pixel Intensity")
        plt.tight_layout()

        st.subheader("Normalized Histograms")
        st.pyplot(fig)
