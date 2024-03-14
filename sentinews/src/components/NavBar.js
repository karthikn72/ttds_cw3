import React, { useEffect, useState } from 'react';
import { onAuthStateChanged, GoogleAuthProvider, signInWithPopup, deleteUser, reauthenticateWithPopup } from 'firebase/auth';
import { doc, deleteDoc } from 'firebase/firestore';
import { Nav, Navbar, Container } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import { auth, db } from './Config/FirebaseConfig';
import { toast } from 'react-toastify';
import globeLogo from '../images/globe-logo.png';

function NavBar() {

    const navigate = useNavigate();
    const provider = new GoogleAuthProvider();

    const [authState, setAuthState] = useState();
    const [showNav, setShowNav] = useState(false);

    useEffect(() => {
        const unsubscribe = onAuthStateChanged(auth, (user) => {
            setAuthState(!!user);
            setShowNav(true);
        });

        return () => unsubscribe();
    }, []);

    const signIn = () => {
        signInWithPopup(auth, provider).then(async () => {
            window.location.reload();
        }).catch((error) => { 
            handleAuthErrors(error.code);
        }); 
    }

    const signOut = () => {
        auth.signOut();
        toast.success("Signed out successfully!", { toastId: 'success-sign-out' }); 
    }

    const deleteAccount = () => {
        const user = auth.currentUser;

        reauthenticateWithPopup(user, provider).then (async () => {
            await deleteDoc(doc(db, process.env.REACT_APP_SAVED_ARTICLES_KEY, auth.currentUser.uid));
            toast.success("Your account has been deleted successfully!", { toastId: 'success-account-delete' }); 
            deleteUser(user); 
            return navigate("/");
        }).catch((error) => {
            handleAuthErrors(error.code);
        })
    }

    const handleAuthErrors = (errorCode) => {
        if (errorCode === "auth/user-disabled") {
            return toast.error("Your account has been disabled. Please try again later.", { toastId: 'user-disabled' });
        } else if (errorCode === "auth/popup-blocked") {
            return toast.error("The Sign In popup was blocked by the browser. Please try again.", { toastId: 'popup-blocked' });
        } else if (errorCode === "auth/popup-closed-by-user" || errorCode === "auth/cancelled-popup-request") {
            return toast.error("The Sign In popup was closed. Please try again.", { toastId: 'popup-closed' });
        } else {
            return toast.error(`Sign in action failed with error code: ${errorCode}.`, { toastId: 'generic-sign-in-error' });
        }
    }

    return(
        <div>
            <Navbar variant="dark" sticky="top" expand="lg" className="py-1" style={{ backgroundColor: "black" }}>
                <Container fluid>
                    <Navbar.Brand as={Link} to={"/"}><img src={globeLogo} width="60px" height="auto" style={{ padding: "5px" }} alt="Sentinews Globe Logo"/></Navbar.Brand>
                    <Navbar.Toggle aria-controls="basic-navbar-nav"/>
                    {showNav ? <Navbar.Collapse id="basic-navbar-nav">
                        <Nav className="ms-auto mb-1">
                            <Nav.Link className='nav-link' as={Link} to={"/daily-digest"}>Daily Digest</Nav.Link>
                            <Nav.Link className='nav-link' as={Link} to={"/saved-articles"}>Saved Articles</Nav.Link>
                            { authState ? <Nav.Link className='nav-link' onClick={deleteAccount}>Delete Account</Nav.Link> : null } 
                            { authState ? <Nav.Link className='nav-link' as={Link} to={"/"} onClick={signOut}>Sign Out</Nav.Link> : <Nav.Link className='nav-link' onClick={signIn}>Sign In</Nav.Link> }
                        </Nav>
                    </Navbar.Collapse> : null }
                </Container>
            </Navbar>
        </div>
    )
}

export default NavBar;