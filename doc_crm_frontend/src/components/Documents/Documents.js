import React, { useState } from 'react';
import './Documents.css';
import * as XLSX from 'xlsx';

const Documents = () => {
  const [formData, setFormData] = useState({
    title: '',
    partnerName: '',
    documentContent: '',
    startDate: '',
    endDate: ''
  });
  const [submitted, setSubmitted] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Handle submission logic here, e.g., sending data to backend or processing locally
    console.log(formData); // For demonstration, log the form data
    setSubmitted(true); // Set submitted to true to display the form data
  };

  const handleExportExcel = () => {
    // Prepare data for export
    const data = [
      ['Title', 'Partner Name', 'Document Content', 'Start Date', 'End Date'],
      [formData.title, formData.partnerName, formData.documentContent, formData.startDate, formData.endDate]
    ];

    const ws = XLSX.utils.aoa_to_sheet(data);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Documents');
    XLSX.writeFile(wb, 'documents.xlsx');
  };

  return (
    <div className="documents-container">
      <form className="documents-form" onSubmit={handleSubmit}>
        <label>Title:</label>
        <input
          type="text"
          name="title"
          value={formData.title}
          onChange={handleChange}
          required
        />

        <label>Partner Name:</label>
        <input
          type="text"
          name="partnerName"
          value={formData.partnerName}
          onChange={handleChange}
          required
        />

        <label>Document Content:</label>
        <textarea
          name="documentContent"
          value={formData.documentContent}
          onChange={handleChange}
          required
        />

        <label>Start Date:</label>
        <input
          type="date"
          name="startDate"
          value={formData.startDate}
          onChange={handleChange}
          required
        />

        <label>End Date:</label>
        <input
          type="date"
          name="endDate"
          value={formData.endDate}
          onChange={handleChange}
          required
        />

        <button type="submit">Create Document</button>
        {submitted && (
          <button type="button" onClick={handleExportExcel}>Export to Excel</button>
        )}
      </form>

      {/* Display form data if submitted */}
      {submitted && (
        <div className="documents-submitted">
          <h2>Submitted Data</h2>
          <p><strong>Title:</strong> {formData.title}</p>
          <p><strong>Partner Name:</strong> {formData.partnerName}</p>
          <p><strong>Document Content:</strong> {formData.documentContent}</p>
          <p><strong>Start Date:</strong> {formData.startDate}</p>
          <p><strong>End Date:</strong> {formData.endDate}</p>
        </div>
      )}
    </div>
  );
};

export default Documents;
