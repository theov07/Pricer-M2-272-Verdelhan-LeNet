# Trinomial Options Pricer

**Advanced options pricing application using trinomial tree model with real-time visualization and convergence analysis.**

*Academic project - Paris Dauphine University - Master 2 in Quantitative Finance*

---

## 🚀 Live Demo

**[→ Access the Web Application](https://option-pricer-verdelhan-lenet.up.railway.app)**

Interactive web interface with real-time pricing, Greeks calculation, and advanced visualizations.

---

## 🎯 Features

- **Options Pricing**: European & American Call/Put options using trinomial tree model
- **Greeks Calculation**: Delta, Gamma, Theta, Vega, Rho with numerical precision
- **Convergence Analysis**: Real-time comparison with Black-Scholes theoretical values
- **Interactive Visualizations**: 
  - D3.js trinomial tree representation
  - Plotly.js convergence charts and sensitivity analysis
- **Advanced Parameters**: Dividend yields, early exercise conditions, pruning thresholds

---

## 📊 Technical Implementation

### Core Financial Models
- **Trinomial Tree**: Cox-Ross-Rubinstein extended model with variable time steps
- **Black-Scholes**: Theoretical benchmark for convergence validation
- **Greeks Computation**: Finite difference methods with adaptive precision
- **Risk Management**: Real-time sensitivity analysis and scenario modeling

### Technology Stack
- **Backend**: Python 3.11, Flask, NumPy, SciPy
- **Frontend**: JavaScript ES6, D3.js, Plotly.js, HTML5/CSS3
- **Deployment**: Docker, Railway.app (cloud hosting)
- **API**: RESTful endpoints with JSON data exchange

---

## 🔬 Usage Options

### Option 1: Web Application (Recommended)
Access the deployed application directly in your browser:
1. Visit **[option-pricer-verdelhan-lenet.up.railway.app](https://option-pricer-verdelhan-lenet.up.railway.app)**
2. Configure option parameters (spot price, strike, volatility, etc.)
3. Run pricing calculations and explore interactive visualizations
4. Analyze convergence behavior and Greeks sensitivity

### Option 2: Local API Development
Clone and run the application locally for development or API integration:

```bash
# Clone repository
git clone https://github.com/theov07/Pricer-M2-272-Verdelhan-LeNet.git
cd Pricer-M2-272-Verdelhan-LeNet

# Install dependencies
pip install -r requirements.txt

# Launch application
python app.py
```

**API Endpoints:**
- `POST /api/calculate` - Options pricing with tree visualization data
- `POST /api/convergence` - Convergence analysis across multiple time steps
- **Base URL**: `http://localhost:5001`

---

## 📈 Academic Context

This project demonstrates practical implementation of advanced financial derivatives pricing models, combining:

- **Mathematical Finance**: Stochastic processes, risk-neutral valuation, numerical methods
- **Software Engineering**: Clean architecture, API design, real-time data visualization
- **Quantitative Analysis**: Model validation, convergence studies, sensitivity analysis

*Developed as part of the Master 2 curriculum in Quantitative Finance at Université Paris Dauphine.*

---

**Authors**: VERDELHAN & LE NET  
**Institution**: Paris Dauphine University - Master 2 Quantitative Finance
