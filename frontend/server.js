const express = require('express');
const bodyParser = require('body-parser');
const path = require('path');
const axios = require('axios');

const app = express();

// Middleware
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public')));

// Set up EJS as the templating engine
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Render Home Page and fetch todos from backend
app.get('/', async (req, res) => {
    try {
        const flaskUrl = "http://backend:5000/todos";
        const response = await axios.get(flaskUrl);
        const todos = response.data || [];
        res.render('index', { todos });
    } catch (error) {
        console.error('Error fetching todos:', error.message);
        res.render('index', { todos: [] });
    }
});

// Handle delete request from frontend
app.post('/delete', async (req, res) => {
    const { id } = req.body;
    if (!id) {
        return res.redirect('/');
    }
    try {
        await axios.delete(`http://backend:5000/todos/${id}`);
    } catch (error) {
        console.error('Delete error:', error.message);
    }
    res.redirect('/');
});

// Render Form Page
app.get('/form', (req, res) => {
    res.render('form', { error: null, success: null });
});

// Handle Form Submission (POST to Flask backend)
app.post('/submit', async (req, res) => {
    const { title, description } = req.body;
    if (!title || !description) {
        return res.render('form', { error: 'All fields are required', success: null });
    }
    try {
        const flaskUrl = process.env.REACT_APP_API_URL || "http://backend:5000/process";
        const response = await axios.post(flaskUrl, { title, description });
        if (response.data && response.data.success) {
            res.render('form', { error: null, success: response.data.message });
        } else {
            res.render('form', { error: 'Submission failed.', success: null });
        }
    } catch (error) {
        console.log('Error:', error.response ? error.response.data : error.message);
        res.render('form', { error: 'Error connecting to backend: ' + error.message, success: null });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Frontend server running on http://localhost:${PORT}`);
});
