import React, {useEffect} from 'react';
import {GLOBAL_SERVER_ERROR} from "./app-util/app-socket";
import {observer} from "mobx-react-lite";
import {configure} from "mobx";
import {createTheme, ThemeProvider} from '@material-ui/core/styles';
import {SnackbarProvider, useSnackbar} from "notistack";
import AppDisplay from "./components/app-display";
import BrowserSettings from "./app-util/local-config";


configure({
    enforceActions: "never",
});

const App = observer(() => {
    const theme = React.useMemo(() =>createTheme({
            palette: {
                type: BrowserSettings.useDarkMode ? 'dark' : 'light',
                primary: {
                    main: '#1976d2',
                },
                secondary: {
                    main: '#ec3434',
                },
            },
        })
        , [BrowserSettings.useDarkMode],
    );

    return (
        <ThemeProvider theme={theme}>
            <SnackbarProvider maxSnack={5}>
                <AppDisplay />
                <NotifyComponent />
            </SnackbarProvider>
        </ThemeProvider>
    );
});


/**
 * Handles listening for notifications, while existing within the DOM for access to the Snackbar component.
 */
const NotifyComponent = observer(() => {
    const { enqueueSnackbar } = useSnackbar();
    const alert = GLOBAL_SERVER_ERROR.get();

    useEffect(() => {
        if (!alert) return;
        const {message, options} = JSON.parse(alert);
        enqueueSnackbar(message, options);
    }, [alert]);

    return <></>
});

export default App;
