let currentUser = null;
let fetchPromise = null;


export async function getCurrentUser() {

    if (currentUser) {
        return currentUser;
    }


    // Prevent duplicate API requests
    if (fetchPromise) {
        return fetchPromise;
    }


    const token = localStorage.getItem("access_token");


    // User is not logged in
    if (!token) {
        return null;
    }


    fetchPromise = (async () => {

        try {

            const response = await fetch(
                "/api/users/me",
                {
                    method: "GET",

                    headers: {
                        "Authorization": `Bearer ${token}`
                    }
                }
            );


            if (response.ok) {

                currentUser = await response.json();

                console.log(
                    "Logged-in user:",
                    currentUser
                );

                return currentUser;
            }


            // Token is invalid/expired
            console.warn(
                "Invalid access token. Removing it."
            );

            localStorage.removeItem("access_token");

            currentUser = null;

            return null;

        } catch (error) {

            console.error(
                "Error fetching current user:",
                error
            );

            currentUser = null;

            return null;

        } finally {

            fetchPromise = null;

        }

    })();


    return fetchPromise;
}


export function logout() {

    localStorage.removeItem("access_token");

    currentUser = null;

    window.location.href = "/";

}


export function getToken() {

    return localStorage.getItem("access_token");

}


export function setToken(token) {

    localStorage.setItem(
        "access_token",
        token
    );

}


export function clearUserCache() {

    currentUser = null;

}