#  Hospital Wait Time Prediction System

##  Project Overview
This project is a comprehensive data science solution designed to manage hospital appointments and predict patient wait times using machine learning. It helps improve patient experience and optimize hospital operations.

##  Problem Statement
Hospitals often face long patient waiting times due to inefficient queue management. There is no system to estimate how long a patient will need to wait.

##  Solution
This system allows patients to book appointments and uses a machine learning model to predict estimated wait time based on:
- Patient priority (Normal/Emergency)
- Department
- Queue position

##  Features
- User Login System (Admin & Patient)
- Doctor & Department Management
- Appointment Booking System
- Emergency Priority Handling
- Wait Time Calculation
- Machine Learning Prediction (Linear Regression)
- Data Visualization (Charts & Analysis)
- Performance Metrics (R², MAE, RMSE)

##  Tech Stack
- Python
- Streamlit
- SQLite
- Pandas
- Scikit-learn
- NumPy

##  Machine Learning Model
- Model: Linear Regression  
- Input Features:
  - Priority
  - Department
  - Queue Position  
- Output:
  - Predicted Wait Time  
- Evaluation Metrics:
  - R² Score
  - Mean Absolute Error (MAE)
  - Root Mean Squared Error (RMSE)

##  Project Structure
hospital-data-science-project/
│
├── README.md
├── capstone_project.ipynb
│
├── src/
│   └── app.py
│
├── data/
│   └── hospital.db
│
├── reports/
│   ├── Technical_Documentation.docx
│   └── Business_Report.docx
│
├── deployment/
│   └── requirements.txt
│
├── presentation/
│   └── presentation.pptx

##  How to Run the Project
1. Clone the repository:
git clone <your-repo-link>

2. Install dependencies:
pip install -r deployment/requirements.txt

3. Run the application:
streamlit run src/app.py

## 📷 Screenshots
(Add screenshots of your app here)

## 📈 Business Impact
- Reduces patient waiting time
- Improves hospital efficiency
- Better queue management
- Enhances patient satisfaction

##  Conclusion
This project demonstrates a complete end-to-end data science workflow, including data handling, machine learning, and deployment. It provides a practical solution to a real-world hospital problem.

##  Author
Alka Kushwaha
