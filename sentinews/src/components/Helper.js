import { auth, db } from "./Config/FirebaseConfig";
import { doc, getDoc } from 'firebase/firestore';

export function getQueryType(query) {
    const booleanSearchRegex = /^\(\s*[^\s,]+(?:\s+[^\s,]+)*\s*,\s*(AND|OR)\s*,\s*[^\s,]+(?:\s+[^\s,]+)*\s*\)$/;
    const proximitySearchRegex = /^\(\s*\w+\s*,\s*\w+\s*,\s*\w+\s*\)$/;
    const publicationSearchRegex = /Publication:.*/i;

    if (query.startsWith('"') && query.endsWith('"')) {
        return "Phrase";
    } else if (booleanSearchRegex.test(query)) {
        return "Boolean";
    } else if (proximitySearchRegex.test(query)) {
        return "Proximity";
    } else if (publicationSearchRegex.test(query)) {
        return "Publication";
    } else {
        return "Freeform";
    }
}

export function paginate(results, articlesPerPage) {
    const pageCount = Math.ceil(results.length / articlesPerPage);
    return Array.from({ length: pageCount }, (_, index) => results.slice(index * articlesPerPage, (index + 1) * articlesPerPage));
}

export async function readStorage(authState) {
    const savedArticlesKey = process.env.REACT_APP_SAVED_ARTICLES_KEY;
    if (authState) {
        const docRef = doc(db, savedArticlesKey, auth.currentUser.uid);
        const docSnap = await getDoc(docRef);
        return docSnap.exists() ? docSnap.data().articles : [];
    } else {
        const articles = localStorage.getItem(savedArticlesKey);
        return articles !== null ? JSON.parse(articles) : [];
    }
}

export const modalStyle = {
    position: "absolute",
    top: "50%",
    left: "50%",
    transform: "translate(-50%, -50%)",
    bgcolor: "background.paper",
    border: "2px solid black",
    boxShadow: 24,
    p: 3,
    overflowY: "scroll"
};