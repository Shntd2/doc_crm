import React, { useState } from 'react';
import './Registration.css';
import axios from 'axios';

const Registration = () => {
  const [formData, setFormData] = useState({
    name: '',
    surname: '',
    companyName: '',
    email: '',
    password: '',
    isRegistering: true,
  });
  const [registrationSuccess, setRegistrationSuccess] = useState(false);
  const [loginSuccess, setLoginSuccess] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleRegistration = async () => {
    try {
      setError(null);  // Clear previous errors
      console.log('Registration Data:', formData);

      const response = await axios.post('http://localhost:5000/registration/api/register', formData, {
        headers: {
          'Content-Type': 'application/json',
        }
      });

      console.log('User registered successfully:', response.data);
      setRegistrationSuccess(true);
    } catch (error) {
      console.error('Error:', error.response ? error.response.data : error.message);
      setError(error.response ? error.response.data.message : 'Network Error');
    }
  };

  const handleLogin = async () => {
    // Implement login logic if needed
  };

  const toggleForm = () => {
    setFormData({
      ...formData,
      isRegistering: !formData.isRegistering,
    });
    setRegistrationSuccess(false);
    setLoginSuccess(false);
    setError(null); // Clear errors when switching forms
  };

  return (
    <div className="user-container">
      {!registrationSuccess && !loginSuccess ? (
        formData.isRegistering ? (
          <form onSubmit={(e) => { e.preventDefault(); handleRegistration(); }}>
            <h2>User Registration</h2>
            {error && <p className="error-message">{error}</p>}
            <div>
              <label htmlFor="name">Name:</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
              />
            </div>
            <div>
              <label htmlFor="surname">Surname:</label>
              <input
                type="text"
                id="surname"
                name="surname"
                value={formData.surname}
                onChange={handleChange}
                required
              />
            </div>
            <div>
              <label htmlFor="companyName">Company Name:</label>
              <input
                type="text"
                id="companyName"
                name="companyName"
                value={formData.companyName}
                onChange={handleChange}
                required
              />
            </div>
            <div>
              <label htmlFor="email">Email:</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>
            <div>
              <label htmlFor="password">Password:</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                pattern="(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}"
                title="Must contain at least one number, one uppercase and lowercase letter, and at least 8 or more characters"
              />
            </div>
            <button type="submit">Register</button>
            <p>Already have an account? <span onClick={toggleForm}>Login here</span></p>
          </form>
        ) : (
          <form onSubmit={(e) => { e.preventDefault(); handleLogin(); }}>
            <h2>User Login</h2>
            <div>
              <label htmlFor="email">Email:</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>
            <div>
              <label htmlFor="password">Password:</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
              />
            </div>
            <button type="submit">Login</button>
            <p>Don't have an account? <span onClick={toggleForm}>Register here</span></p>
          </form>
        )
      ) : (
        <div className="success-message">
          <p>{registrationSuccess ? 'You have registered successfully!' : 'You have logged in successfully!'}</p>
        </div>
      )}
    </div>
  );
};

export default Registration;
