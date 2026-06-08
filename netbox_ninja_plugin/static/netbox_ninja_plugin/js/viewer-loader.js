function ninjaDarkMode() {
    const theme = document.documentElement.getAttribute('data-bs-theme');
    if (theme === 'dark' || theme === 'light') {
        return theme;
    }
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        return 'dark';
    }
    return 'light';
}

function updateMxGraphData(configs) {
    for (const config of configs) {
        const src = config.viewerScriptUrl;
        const xmlData = config.xmlData;
        const editUrl = config.editUrl;
        const mxgraphContainerId = config.mxgraphContainerId;

        const mxgraphContainer = document.getElementById(mxgraphContainerId);
        if (!mxgraphContainer) {
            continue;
        }

        const graphDiv = document.createElement('div');
        graphDiv.setAttribute('class', 'mxgraph');
        graphDiv.setAttribute('style', 'max-width:100%; max-height:100%; border:5px solid transparent;');

        const data = {
            highlight: '#0000ff',
            nav: false,
            resize: true,
            toolbar: 'zoom lightbox',
            edit: editUrl,
            xml: xmlData,
            'dark-mode': ninjaDarkMode(),
        };
        graphDiv.setAttribute('data-mxgraph', JSON.stringify(data));
        mxgraphContainer.appendChild(graphDiv);

        const mxscript = document.createElement('script');
        mxscript.type = 'text/javascript';
        mxscript.src = src;
        mxgraphContainer.appendChild(mxscript);
    }
}

function reloadMxGraphViewers(configs) {
    for (const config of configs) {
        const mxgraphContainer = document.getElementById(config.mxgraphContainerId);
        if (mxgraphContainer) {
            mxgraphContainer.innerHTML = '';
        }
    }
    updateMxGraphData(configs);
}

let ninjaThemeReloadTimer = null;

function scheduleNinjaDiagramThemeReload(configs) {
    if (ninjaThemeReloadTimer !== null) {
        clearTimeout(ninjaThemeReloadTimer);
    }
    ninjaThemeReloadTimer = setTimeout(function () {
        ninjaThemeReloadTimer = null;
        reloadMxGraphViewers(configs);
    }, 150);
}

function watchNinjaDiagramTheme(configs) {
    const observer = new MutationObserver(function (mutations) {
        for (const mutation of mutations) {
            if (mutation.attributeName === 'data-bs-theme') {
                scheduleNinjaDiagramThemeReload(configs);
                return;
            }
        }
    });
    observer.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['data-bs-theme'],
    });

    window.addEventListener('storage', function (event) {
        if (event.key === 'netbox-color-mode') {
            scheduleNinjaDiagramThemeReload(configs);
        }
    });
}

document.addEventListener('DOMContentLoaded', function () {
    const configs = window.NINJA_CONFIGS;
    if (!configs) {
        return;
    }
    updateMxGraphData(configs);
    watchNinjaDiagramTheme(configs);
}, false);
