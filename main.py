import streamlit as st
import numpy as np
import trimesh
import plotly.graph_objects as go
import cv2

# Streamlit App Title
st.title("Cellular Lattice to Volumetric Shape Converter")

# Sidebar for User Options
st.sidebar.header("Options")
shape_choice = st.sidebar.selectbox("Select the volumetric shape", ["Cube", "Cylinder", "Sphere"])

# User Inputs for Shape Parameters
if shape_choice == "Cube":
    length = st.sidebar.number_input("Edge Length (mm)", value=10.0, step=1.0, min_value=1.0)
elif shape_choice == "Cylinder":
    radius = st.sidebar.number_input("Radius (mm)", value=5.0, step=1.0, min_value=1.0)
    height = st.sidebar.number_input("Height (mm)", value=10.0, step=1.0, min_value=1.0)
elif shape_choice == "Sphere":
    radius = st.sidebar.number_input("Radius (mm)", value=5.0, step=1.0, min_value=1.0)

# Upload Image
uploaded_file = st.file_uploader("Upload Cellular Lattice Image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Load the image
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)

    st.subheader("Uploaded Cellular Lattice Image")
    st.image(image, caption="Cellular Lattice Structure", use_column_width=True)
    
    # Thresholding to extract lattice 
    _, thresholded = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    
    # Show Preprocessed Image
    st.subheader("Thresholded Image for Lattice Structure")
    st.image(thresholded, caption="Processed Cellular Lattice", use_column_width=True)

    # Generate 3D Shape
    st.subheader("Generated Volumetric Shape")
    if shape_choice == "Cube":
        mesh = trimesh.creation.box(extents=(length, length, length))
    elif shape_choice == "Cylinder":
        mesh = trimesh.creation.cylinder(radius=radius, height=height)
    elif shape_choice == "Sphere":
        mesh = trimesh.creation.icosphere(radius=radius)
    
    # Convert Trimesh to Plotly Mesh3D
    vertices = np.array(mesh.vertices)
    faces = np.array(mesh.faces)
    x, y, z = vertices[:, 0], vertices[:, 1], vertices[:, 2]
    i, j, k = faces[:, 0], faces[:, 1], faces[:, 2]

    fig = go.Figure(
        data=[go.Mesh3d(
                x=x,
                y=y,
                z=z,
                i=i,
                j=j,
                k=k,
                opacity=0.5,
                color="cyan"
            )]
    )
    fig.update_layout(
        scene=dict(aspectmode="data"),
        margin=dict(l=0, r=0, b=0, t=0)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Provide Download Option for the 3D Model
    st.subheader("Download the 3D Model")
    model_bytes = mesh.export(file_type='stl')
    st.download_button("Download STL File", model_bytes, file_name="volumetric_shape.stl")
