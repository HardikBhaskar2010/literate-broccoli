import React from 'react';
import { AuthProvider } from './contexts/AuthContext';
import InstagramLogin from './components/InstagramLogin';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <div className="App">
        <InstagramLogin />
      </div>
    </AuthProvider>
  );
}

export default App;