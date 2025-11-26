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
# API URL (Auto-detect based on environment)
# -----------------------------
# Use Render API (working accurately) or Railway API
# For local API development, set environment variable: API_URL=http://localhost:8000
API_URL = os.getenv("API_URL", "https://mlp-summative-2.onrender.com")

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
    """Check if API is running and model is loaded"""
    try:
        response = requests.get(f"{API_URL}/", timeout=10)
        if response.status_code == 200:
            try:
                data = response.json() if response.content else {}
                model_loaded = data.get("model_loaded")
                # If model_loaded is not in response, check /health endpoint
                if model_loaded is None:
                    try:
                        health_response = requests.get(f"{API_URL}/health", timeout=5)
                        if health_response.status_code == 200:
                            health_data = health_response.json()
                            model_loaded = health_data.get("model_loaded", True)  # Default to True if API responds
                    except:
                        # If health check fails, assume model is loaded if API responds (predictions work)
                        model_loaded = True
                return True, data.get("message", "API is running"), model_loaded if model_loaded is not None else True
            except Exception as json_error:
                # If JSON parsing fails, but status is 200, API is up
                # Since predictions work, model is likely loaded
                return True, "API is running", True
        return False, f"API returned status {response.status_code}", False
    except requests.exceptions.Timeout:
        return False, "API is not responding (Timeout)", False
    except requests.exceptions.ConnectionError:
        return False, "API is not responding (Connection Error)", False
    except Exception as e:
        return False, f"API check failed: {str(e)}", False

def get_model_uptime():
    """Get model uptime information"""
    is_up, message, model_loaded = check_api_status()
    return is_up, message, datetime.now(), model_loaded

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
    is_up, message, current_time, model_loaded = get_model_uptime()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if is_up:
            st.success("**Online**")
        else:
            st.error("**Offline**")
    
    with col2:
        st.info(f"**Status:** {message}")
        if is_up and not model_loaded:
            st.warning("Model not loaded")
    
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
                
                try:
                    response = requests.post(
                        f"{API_URL}/predict",
                        files={"file": ("image.png", img_bytes, "image/png")},
                        timeout=30
                    )
                except requests.exceptions.Timeout:
                    st.error("Request timed out. The API is taking too long to respond. Please try again or check if the API is running.")
                    return
                except requests.exceptions.ConnectionError:
                    st.error(f"Could not connect to API at {API_URL}. Please check if the API is running and accessible.")
                    return
                except Exception as e:
                    st.error(f"Request failed: {str(e)}")
                    return

            if response.status_code == 200:
                result = response.json()
                prediction = result.get('prediction', 'Unknown')
                all_probs = result.get('all_probabilities', {})
                confidence = result.get('confidence', 0.0)
                
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
                # Show detailed error message from API
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', 'Unknown error')
                    suggestion = error_data.get('suggestion', '')
                    
                    st.error(f"**Prediction failed (Status {response.status_code})**: {error_msg}")
                    if suggestion:
                        st.info(f"**Suggestion**: {suggestion}")
                    if response.status_code == 503:
                        st.warning("The model is not loaded. You may need to use the /retrain endpoint to train a model first, or check Railway logs for model loading errors.")
                except:
                    st.error(f"Prediction failed with status {response.status_code}. Response: {response.text[:200]}")


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
            with st.spinner("Uploading images and retraining model... This may take a few minutes..."):
                files = []
                for f in uploaded_files:
                    # Read file bytes for requests
                    file_bytes = f.read()
                    # Reset file pointer for potential reuse
                    f.seek(0)
                    # Use proper MIME type
                    mime_type = f.type if f.type else "image/jpeg"
                    files.append(("files", (f.name, file_bytes, mime_type)))

                try:
                    response = requests.post(
                        f"{API_URL}/retrain",
                        files=files,
                        timeout=600
                    )
                except requests.exceptions.Timeout:
                    st.error("Request timed out. Retraining takes time - try again or check API logs.")
                    return
                except Exception as e:
                    st.error(f"Request failed: {str(e)}")
                    return

                if response.status_code == 200:
                    result = response.json()
                    st.success("Model retrained successfully!")
                    st.markdown("### Training Results")
                    st.write(f"**Final Train Accuracy:** {result.get('final_train_accuracy', 0):.4f}")
                    st.write(f"**Final Validation Accuracy:** {result.get('final_val_accuracy', 0):.4f}")
                    st.write(f"**Epochs Trained:** {result.get('epochs_trained', 0)}")
                    st.write(f"**Files Uploaded:** {result.get('uploaded_files', 0)}")
                else:
                    st.error(f"Error {response.status_code}: {response.text}")


# VISUALIZATIONS PAGE
def visualizations_page():
    st.markdown("<h2 style='color:#4169E1;'>Data Visualizations</h2>", unsafe_allow_html=True)
    
    st.write("Explore insights from the vegetable image dataset through feature analysis.")
    
    # Check if data directory exists - try multiple possible locations
    train_dir = None
    possible_paths = ["data/train", "data/train_min", "../data/train", "./data/train"]
    
    for path in possible_paths:
        if os.path.exists(path):
            train_dir = path
            break
    
    if not train_dir:
        st.info("**Note:** Training data directory not found in this deployment. Visualizations require access to the training images. This feature is available when running locally with the full dataset.")
        st.write("The visualizations demonstrate three key features:")
        st.markdown("""
        1. **Image Brightness Distribution** - Shows brightness levels across vegetable images
        2. **Aspect Ratio Distribution** - Shows width-to-height ratios of images  
        3. **Edge Density Distribution** - Measures texture complexity through edge detection
        """)
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
                if not train_dir:
                    break
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
                if not train_dir:
                    break
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
                if not train_dir:
                    break
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
try:
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Predict", "Retrain", "Visualizations"])

    # API Status in Sidebar
    st.sidebar.divider()
    st.sidebar.markdown("### API Status")
    try:
        is_up, message, model_loaded = check_api_status()
        if is_up:
            st.sidebar.success("Online")
            if not model_loaded:
                st.sidebar.warning("Model not loaded")
        else:
            st.sidebar.error("Offline")
    except Exception as e:
        st.sidebar.warning(f"API check failed")

    # Route to appropriate page
    if page == "Home":
        home_page()
    elif page == "Predict":
        prediction_page()
    elif page == "Retrain":
        retrain_page()
    elif page == "Visualizations":
        visualizations_page()
except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.write("Please refresh the page or check the logs.")
    import traceback
    with st.expander("Error Details (for debugging)"):
        st.code(traceback.format_exc())