import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';

import NavBar from './components/NavBar';
import Error404 from './components/Error404';
import Landing from './components/Landing';
import Results from './components/Results';
import Digest from './components/Digest';
import SavedArticles from './components/SavedArticles';

import './App.css';
import 'react-toastify/dist/ReactToastify.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'react-date-range/dist/styles.css';
import 'react-date-range/dist/theme/default.css';

function App() {
    return (
        <div className="App">
            <BrowserRouter>
                <NavBar/>
                <Routes>
                    <Route path="/" element={<Landing/>}/>
                    <Route path="/*" element={<Error404/>}/>
                    <Route path="/search" element={<Results/>}/>
                    <Route path="/daily-digest" element={<Digest/>}/>
                    <Route path="/saved-articles" element={<SavedArticles/>}/>
                </Routes>
            </BrowserRouter>
            <ToastContainer position='top-right' autoClose={2500} pauseOnHover={false} draggable stacked/>
        </div>
    );
}

export default App;
