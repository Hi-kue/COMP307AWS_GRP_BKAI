const routes = {
    "/": {
        linkLabel: "Home",
        path: "src/index.html",
        content: ""
    },
    "/login": {
        linkLabel: "Login",
        path: "src/pages/auth/login.html",
        content: ""
    },
    "/register": {
        linkLabel: "Register",
        path: "src/pages/auth/register.html",
        content: ""
    },
    "/movies": {
        linkLabel: "Movies",
        path: "src/pages/movies/movies.html",
        content: ""
    },
    "/movies/detail": {
        linkLabel: "Movie Details",
        path: "src/pages/movies/movies-detail.html",
        content: ""
    },
    "/movies/search": {
        linkLabel: "Movie Search",
        path: "src/pages/movies/movies-search.html",
        content: ""
    },
    "/movies/upload": {
        linkLabel: "Movie Upload",
        path: "src/pages/movies/movies-upload.html",
        content: ""
    },
    "/movies/edit": {
        linkLabel: "Movie Edit",
        path: "src/pages/movies/movies-edit.html",
        content: ""
    }
};

const app = document.querySelector("#app");
const nav = document.querySelector("#nav");

const fetchRouteContent = async (route) => {
    const response = await fetch(routes[route].path);
    const content = await response.text();
    routes[route].content = content;
};

const loadAllRoutesContent = async () => {
    for (const route in routes) {
        await fetchRouteContent(route);
    }
};

const renderNavigationLinks = () => {
    const navFragment = document.createDocumentFragment();
    Object.keys(routes).forEach(route => {
        const link = document.createElement("a");
        link.href = route;
        link.textContent = routes[route].linkLabel;
        link.setAttribute("data-route", route);
        navFragment.appendChild(link);
    });
    nav.appendChild(navFragment);
};

const registerNavigationLinks = () => {
    nav.addEventListener("click", (e) => {
        e.preventDefault();
        const route = e.target.getAttribute("data-route");

        if (route) {
            history.pushState({}, "", route);
            renderContent(route);
        }
    });
};

const renderContent = (route) => {
    app.innerHTML = routes[route]?.content || "<p>Page not found</p>";
};

const navigate = (e) => {
    const route = e.target.pathname;
    history.pushState({}, "", route);
    renderContent(route);
};

const registerBrowserBackAndForth = () => {
    window.onpopstate = () => {
        const route = location.pathname;
        renderContent(route);
    };
};

const renderInitialPage = () => {
    const route = location.pathname;
    renderContent(route);
};

(async function bootup() {
    await loadAllRoutesContent();
    renderNavigationLinks();
    registerNavigationLinks();
    registerBrowserBackAndForth();
    renderInitialPage();
})();