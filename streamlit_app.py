import streamlit as st
import requests
from PIL import Image, ImageFilter
import io
import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import time

# -----------------------------
# API URL (Change when deployed)
# -----------------------------
API_URL = "https://mlp-summative-2.onrender.com"

# Class names matching the model
CLASS_NAMES = [
    "Bean", "Bitter_Gourd", "Bottle_Gourd", "Brinjal", "Broccoli",
    "Cabbage", "Capsicum", "Carrot", "Cauliflower", "Cucumber",
    "Papaya", "Potato", "Pumpkin", "Radish", "Tomato"
]


# -----------------------------
# Helper Functions
# -----------------------------
def check_api_status():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_URL}/", timeout=10)
        return response.status_code == 200, response.json().get("message", "API is running")
    except:
        return False, "API is not responding"

def get_model_uptime():
    """Get model uptime information"""
    is_up, message = check_api_status()
    return is_up, message, datetime.now()

# HOME PAGE
def home_page():
    st.markdown("""
        <h1 style='text-align: center; color:#2E8B57;'>Vegetable Classification System</h1>
        <p style='text-align: center; font-size:18px;'>
            A smart AI-powered system that helps identify different vegetable types and allows 
            retraining the model with new image data.
        </p>
        <br>
    """, unsafe_allow_html=True)

    # Model Uptime Status
    st.markdown("### Model Status")
    is_up, message, current_time = get_model_uptime()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if is_up:
            st.success("**Online**")
        else:
            st.error("**Offline**")
    
    with col2:
        st.info(f"**Status:** {message}")
    
    with col3:
        st.info(f"**Last Check:** {current_time.strftime('%H:%M:%S')}")
    
    # Auto-refresh status
    if st.button("Refresh Status"):
        st.rerun()

    st.markdown("""
        ### What you can do here:
        - **Predict the type of vegetable** from an uploaded image  
        - **Retrain the model** with new image data  
        - **View data visualizations** and insights
        - **Monitor model performance** and uptime
    """)

    # Model Information
    st.markdown("### Model Information")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Classes", len(CLASS_NAMES))
        st.metric("Supported Formats", "JPG, PNG, JPEG")
    with col2:
        st.metric("API Endpoint", API_URL)
        st.metric("Model Type", "CNN (Convolutional Neural Network)")
    
    st.markdown("### Supported Vegetable Classes")
    cols = st.columns(5)
    for i, veg in enumerate(CLASS_NAMES):
        with cols[i % 5]:
            st.write(f"• {veg}")


# PREDICTION PAGE
def prediction_page():
    st.markdown("<h2 style='color:#228B22;'>Predict Vegetable Class</h2>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload an image of a vegetable", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        col1, col2 = st.columns([1, 1])
        with col1:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_container_width=True)

        if st.button("Predict", type="primary"):
            with st.spinner("Analyzing image..."):
                img_bytes = io.BytesIO()
                image.save(img_bytes, format="PNG")
                img_bytes = img_bytes.getvalue()
                
                response = requests.post(
                    f"{API_URL}/predict",
                    files={"file": ("image.png", img_bytes, "image/png")},
                    timeout=30
                )

            if response.status_code == 200:
                result = response.json()
                prediction = result['prediction']
                all_probs = result.get('all_probabilities', {})
                
                # Main prediction result
                st.markdown("---")
                st.markdown("### Prediction Result")
                
                st.success(f"### **{prediction}**")
                
                # Top predictions bar chart
                if all_probs:
                    # Sort by probability
                    sorted_probs = sorted(all_probs.items(), key=lambda x: x[1], reverse=True)
                    top_5 = sorted_probs[:5]
                    
                    st.markdown("### Prediction Analysis")
                    
                    # Create bar chart for top predictions
                    classes = [item[0] for item in top_5]
                    probs = [item[1] * 100 for item in top_5]  # Convert to percentage
                    
                    fig, ax = plt.subplots(figsize=(10, 6))
                    colors = ['#2E8B57' if i == 0 else '#90EE90' for i in range(len(classes))]
                    bars = ax.barh(classes, probs, color=colors, alpha=0.8, edgecolor='black')
                    ax.set_xlabel('Confidence (%)', fontsize=12, fontweight='bold')
                    ax.set_ylabel('Vegetable Class', fontsize=12, fontweight='bold')
                    ax.set_title('Top 5 Predictions with Confidence Scores', fontsize=14, fontweight='bold')
                    ax.set_xlim(0, 100)
                    
                    # Add percentage labels on bars
                    for i, (bar, prob) in enumerate(zip(bars, probs)):
                        width = bar.get_width()
                        ax.text(width + 1, bar.get_y() + bar.get_height()/2, 
                               f'{prob:.1f}%', ha='left', va='center', fontweight='bold')
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                    
                    # Detailed breakdown table
                    st.markdown("#### Complete Prediction Breakdown")
                    prob_data = []
                    for veg, prob in sorted_probs:
                        prob_data.append({
                            "Vegetable": veg,
                            "Confidence": f"{prob*100:.2f}%",
                            "Probability": prob
                        })
                    
                    import pandas as pd
                    df = pd.DataFrame(prob_data)
                    df = df.sort_values('Probability', ascending=False)
                    st.dataframe(df[["Vegetable", "Confidence"]], use_container_width=True, hide_index=True)
                    
                    # Insights
                    st.markdown("#### Analysis Insights")
                    if len(top_5) > 0:
                        top_confidence = top_5[0][1]
                        if top_confidence > 0.9:
                            st.info(f"**High Confidence**: The model is highly confident this is **{prediction}**. This is a very reliable prediction.")
                        elif top_confidence > 0.7:
                            st.warning(f"**Moderate Confidence**: The model shows moderate confidence for **{prediction}**. Consider reviewing the top alternatives.")
                        else:
                            st.warning(f"**Low Confidence**: The model shows low confidence for **{prediction}**. The image might be unclear or ambiguous.")
                    
                    if len(top_5) > 1:
                        second_place = top_5[1]
                        diff = (top_5[0][1] - second_place[1]) * 100
                        if diff < 10:
                            st.info(f"**Close Call**: The prediction is close between **{top_5[0][0]}** ({top_5[0][1]*100:.1f}%) and **{second_place[0]}** ({second_place[1]*100:.1f}%). Difference: {diff:.1f}%")
            else:
                st.error("Prediction failed. Please check your API.")


# RETRAIN PAGE
def retrain_page():
    st.markdown("<h2 style='color:#800000;'>Retrain Model</h2>", unsafe_allow_html=True)

    st.info("**Note:** Upload multiple vegetable images. The model will be retrained from scratch using the existing training data plus your uploaded images.")

    uploaded_files = st.file_uploader(
        "Upload training images",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )

    if st.button("Start Retraining", type="primary"):
        if not uploaded_files:
            st.error("Please upload at least one image.")
        else:
            with st.spinner("Uploading images and retraining model..."):

                files = []
                for f in uploaded_files:
                    files.append(("files", (f.name, f, f"type/{f.type.split('/')[-1]}")))

                response = requests.post(f"{API_URL}/retrain", files=files, timeout=600)

                if response.status_code == 200:
                    st.success("Model retrained successfully!")
                else:
                    st.error(f"Error: {response.text}")


# VISUALIZATIONS PAGE
def visualizations_page():
    st.markdown("<h2 style='color:#4169E1;'>Data Visualizations</h2>", unsafe_allow_html=True)
    
    st.write("Explore insights from the vegetable image dataset through feature analysis.")
    
    # Check if data directory exists
    train_dir = "data/train"
    if not os.path.exists(train_dir):
        st.warning("Training data directory not found. Visualizations require the data/train directory.")
        return
    
    # Feature 1: Brightness Distribution
    st.markdown("### Feature 1: Image Brightness Distribution")
    st.write("**Interpretation:** This shows the distribution of brightness levels across vegetable images. "
             "Different vegetables may have different natural brightness levels, which can help the model distinguish between classes.")
    
    if st.button("Generate Brightness Distribution", key="brightness"):
        with st.spinner("Analyzing brightness..."):
            brightness_values = []
            sample_count = 0
            max_samples = 500  # Limit for performance
            
            for cls in CLASS_NAMES[:5]:  # Sample from first 5 classes
                folder = os.path.join(train_dir, cls)
                if os.path.exists(folder):
                    for img_file in os.listdir(folder)[:100]:
                        if sample_count >= max_samples:
                            break
                        try:
                            img_path = os.path.join(folder, img_file)
                            img = Image.open(img_path).convert('L')
                            brightness_values.append(np.mean(np.array(img)))
                            sample_count += 1
                        except:
                            continue
                    if sample_count >= max_samples:
                        break
            
            if brightness_values:
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.hist(brightness_values, bins=30, edgecolor='black', alpha=0.75, color='skyblue')
                ax.set_title("Brightness Distribution of Vegetable Images", fontsize=14, fontweight='bold')
                ax.set_xlabel("Brightness Level", fontsize=12)
                ax.set_ylabel("Frequency", fontsize=12)
                ax.grid(axis='y', linestyle='--', alpha=0.5)
                plt.tight_layout()
                st.pyplot(fig)
                st.caption(f"Analyzed {len(brightness_values)} images")
            else:
                st.error("Could not load images for analysis.")
    
    st.divider()
    
    # Feature 2: Aspect Ratio Distribution
    st.markdown("### Feature 2: Aspect Ratio Distribution")
    st.write("**Interpretation:** This shows the width-to-height ratios of images. "
             "Different vegetables may be photographed at different orientations, creating distinct aspect ratio patterns.")
    
    if st.button("Generate Aspect Ratio Distribution", key="aspect"):
        with st.spinner("Analyzing aspect ratios..."):
            ratios = []
            sample_count = 0
            max_samples = 500
            
            for cls in CLASS_NAMES[:5]:
                folder = os.path.join(train_dir, cls)
                if os.path.exists(folder):
                    for img_file in os.listdir(folder)[:100]:
                        if sample_count >= max_samples:
                            break
                        try:
                            img_path = os.path.join(folder, img_file)
                            with Image.open(img_path) as im:
                                w, h = im.size
                                ratios.append(w / h)
                                sample_count += 1
                        except:
                            continue
                    if sample_count >= max_samples:
                        break
            
            if ratios:
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.hist(ratios, bins=30, edgecolor='black', alpha=0.75, color='lightgreen')
                ax.set_title("Aspect Ratio Distribution of Vegetable Images", fontsize=14, fontweight='bold')
                ax.set_xlabel("Width / Height Ratio", fontsize=12)
                ax.set_ylabel("Frequency", fontsize=12)
                ax.grid(axis='y', linestyle='--', alpha=0.5)
                plt.tight_layout()
                st.pyplot(fig)
                st.caption(f"Analyzed {len(ratios)} images")
            else:
                st.error("Could not load images for analysis.")
    
    st.divider()
    
    # Feature 3: Edge Density (Texture)
    st.markdown("### Feature 3: Edge Density (Texture Feature)")
    st.write("**Interpretation:** This measures texture complexity through edge detection. "
             "Different vegetables have different surface textures (smooth vs. rough), which helps the model identify them.")
    
    if st.button("Generate Edge Density Distribution", key="edges"):
        with st.spinner("Analyzing texture/edges... This may take a moment..."):
            edges = []
            sample_count = 0
            max_samples = 300  # Fewer for performance (edge detection is slower)
            
            for cls in CLASS_NAMES[:5]:
                folder = os.path.join(train_dir, cls)
                if os.path.exists(folder):
                    for img_file in os.listdir(folder)[:60]:
                        if sample_count >= max_samples:
                            break
                        try:
                            img_path = os.path.join(folder, img_file)
                            img = Image.open(img_path).convert("L")
                            edges_img = img.filter(ImageFilter.FIND_EDGES)
                            edges.append(np.mean(np.array(edges_img)))
                            sample_count += 1
                        except:
                            continue
                    if sample_count >= max_samples:
                        break
            
            if edges:
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.hist(edges, bins=30, edgecolor='black', alpha=0.75, color='salmon')
                ax.set_title("Edge Density Distribution (Texture Feature)", fontsize=14, fontweight='bold')
                ax.set_xlabel("Edge Density Value", fontsize=12)
                ax.set_ylabel("Frequency", fontsize=12)
                ax.grid(axis='y', linestyle='--', alpha=0.5)
                plt.tight_layout()
                st.pyplot(fig)
                st.caption(f"Analyzed {len(edges)} images")
            else:
                st.error("Could not load images for analysis.")

# -----------------------------
# SIDEBAR NAVIGATION
# -----------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Predict", "Retrain", "Visualizations"])

# API Status in Sidebar
st.sidebar.divider()
st.sidebar.markdown("### API Status")
is_up, message = check_api_status()
if is_up:
    st.sidebar.success("Online")
else:
    st.sidebar.error("Offline")

if page == "Home":
    home_page()
elif page == "Predict":
    prediction_page()
elif page == "Retrain":
    retrain_page()
elif page == "Visualizations":
    visualizations_page()