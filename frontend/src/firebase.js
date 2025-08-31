// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyBAK4fizcDusgEIBfiJh9hzEi-fxHviXl4",
  authDomain: "agent-x-32580.firebaseapp.com",
  projectId: "agent-x-32580",
  storageBucket: "agent-x-32580.firebasestorage.app",
  messagingSenderId: "685824995732",
  appId: "1:685824995732:web:0c83f0516f109944025f81"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Authentication and get a reference to the service
export const auth = getAuth(app);

// Initialize Cloud Firestore and get a reference to the service
export const db = getFirestore(app);

export default app;