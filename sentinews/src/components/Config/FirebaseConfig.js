import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

const firebaseConfig = {
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY,
  authDomain: "sentinews-413116.firebaseapp.com",
  projectId: "sentinews-413116",
  storageBucket: "sentinews-413116.appspot.com",
  messagingSenderId: "38655714619",
  appId: "1:38655714619:web:018f3fa7255dff8c80831e"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

export { auth, db }; 