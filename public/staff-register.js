import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getAuth, createUserWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";
import { getFirestore, doc, setDoc } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";

const firebaseConfig = {
  apiKey: "AIzaSyBLh8hwA1_asveSxisiZyRMbi-So7t1rE0",
  authDomain: "medical-triage-system-5685f.firebaseapp.com",
  projectId: "medical-triage-system-5685f",
  storageBucket: "medical-triage-system-5685f.firebasestorage.app",
  messagingSenderId: "1043408410847",
  appId: "1:1043408410847:web:9ebdf47a2d02af006bb16a"
};
const app=initializeApp(firebaseConfig);
const auth=getAuth(app);
const db=getFirestore(app);

window.registerStaff=async function(){
 const email=document.getElementById("reg-email").value.trim();
 const pass=document.getElementById("reg-password").value.trim();
 const role=document.getElementById("reg-role").value;

 try{
   const user=await createUserWithEmailAndPassword(auth,email,pass);
   await setDoc(doc(db,"staff",user.user.uid),{email,role});
   alert("Staff Registered");
   window.location.href="staff-login.html";
 }catch(e){alert(e.message);}
}

window.goToLogin=function(){window.location.href="staff-login.html";}
