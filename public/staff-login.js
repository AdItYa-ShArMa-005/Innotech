import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getAuth, signInWithEmailAndPassword, sendPasswordResetEmail } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";
import { getFirestore, doc, getDoc } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";

const firebaseConfig = {
  apiKey: "AIzaSyBLh8hwA1_asveSxisiZyRMbi-So7t1rE0",
  authDomain: "medical-triage-system-5685f.firebaseapp.com",
  projectId: "medical-triage-system-5685f",
  storageBucket: "medical-triage-system-5685f.firebasestorage.app",
  messagingSenderId: "1043408410847",
  appId: "1:1043408410847:web:9ebdf47a2d02af006bb16a"
};
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

window.staffLogin = async function(){
 const email=document.getElementById('email').value.trim();
 const password=document.getElementById('password').value.trim();
 const role=document.getElementById('role').value;

 try{
   const userCred=await signInWithEmailAndPassword(auth,email,password);
   const ref=doc(db,"staff",userCred.user.uid);
   const snap=await getDoc(ref);
   if(!snap.exists()){alert("No staff profile found");return;}
   if(snap.data().role!==role){alert("Role mismatch");return;}
   localStorage.setItem("staffUID",userCred.user.uid);
   localStorage.setItem("staffRole",role);
   window.location.href="index.html";
 }catch(e){alert(e.message);}
}

window.goToReset=function(){
 const email=prompt("Enter email");
 if(!email)return;
 sendPasswordResetEmail(auth,email).then(()=>alert("Sent")).catch(e=>alert(e.message));
}

window.goToRegister=function(){window.location.href="staff-register.html";}
