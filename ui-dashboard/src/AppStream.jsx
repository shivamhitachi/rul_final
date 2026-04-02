/**
 * @file      : AppStream.jsx
 * @summary   : This is the component that manages the app stream.
 * @author    : Charles Best <cbest@nvidia.com>
 * @created   : 2023-12-14
 * @copywrite : 2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
 * @exports   : AppStream
 */

import React from "react";
import PropTypes from 'prop-types';

//import PlaceholderImage from './assets/purse.png';
// --- BYPASSED FOR VM TESTING ---
// import AppStreamer from '../../web-streaming-library/src/AppStreamer';
// import { AppStreamer } from '@nvidia/omniverse-webrtc-streaming-library';

export default class AppStream extends React.Component {
    constructor(props) {
        super(props);

        this._requested = false;
        this.state      = {
            streamReady : false
        };
    }

    /**
     * @function componentDidMount
     */
    componentDidMount() {
        if ( !this._requested ) {
            this._requested = true;

            let streamConfig = {};

            if ( this.props.streamConfig.source === 'gfn' ) {
                streamConfig = this.props.streamConfig;
            }
            if ( this.props.streamConfig.source === 'local' ) {
                // No login necessary - pass back a dummy user to the window.
                this.props.onLoggedIn('localUser');

                streamConfig = {
                    source           : 'local',
                    videoElementId   : 'remote-video',
                    audioElementId   : 'remote-audio',
                    messageElementId : 'message-display',
                    urlLocation      : {search: 'server=127.0.0.1&resolution=1920:1080&fps=60&mic=0&cursor=free&autolaunch=true'}
                };
            }

            // --- BYPASSED FOR VM TESTING ---
            // Commented out the actual NVIDIA connection logic
            /*
            try {
                AppStreamer.setup({
                    streamConfig : streamConfig,
                    onUpdate     : (message) =>this._onUpdate(message),
                    onStart      : (message) =>this._onStart (message),
                    onCustomEvent: (message) =>this._onCustomEvent (message)
                })
                .then((result) => {
                    console.info(result);
                })
                .catch((error) => {
                    console.error(error);
                });
            }
            catch ( error ) {
                console.error(error);
            }
            */

            // SIMULATE A SUCCESSFUL CONNECTION SO THE UI RENDERS
            setTimeout(() => {
                console.info('[VM Bypass] Simulating streamReady');
                this.setState({streamReady: true});
                this.props.onStarted();
            }, 1000);
            // --------------------------------
        }
    }

    componentDidUpdate(prevProps, prevState, snapshot) {
        if ( prevState.streamReady === false && this.state.streamReady === true ) {
            const player = document.getElementById("gfn-stream-player-video");

            if ( player ) {
                player.tabIndex    = "-1";
                player.playsInline = true;
                player.muted       = true;
                player.play();
            }
        }
    }

    /**
     * @function sendMessage
     */
    static sendMessage(message, storeSelection) {
        // --- BYPASSED FOR VM TESTING ---
        /*
        AppStreamer.sendMessage(
            message,
            storeSelection
        );
        */
        console.log("[VM Bypass] Suppressed sendMessage to stream:", message);
        // --------------------------------
    }

    _onStart(message) {
        if ( message.action === 'start' && message.status === 'success' && !this.state.streamReady ) {
            console.info('streamReady');
            this.setState({streamReady: true});
            this.props.onStarted();
        }

        console.debug(message);
    }

    _onUpdate(message) {
        try {
            if ( message.action === 'authUser' && message.status === 'success' ) {
                this.props.onLoggedIn(message.info);
            }
        }
        catch ( error ) {
            console.error(message);
        }
    }

    _onCustomEvent(message) {
        this.props.handleCustomEvent(message)
    }

    render() {
        if ( this.props.streamConfig.source === 'gfn' ) {
            return (
                <div
                    id    = "view"
                    style = {{
                        backgroundColor: 'black',
                        display: 'flex', justifyContent: 'space-between',
                        ...this.props.style
                    }}
                />
            );
        }
        else if ( this.props.streamConfig.source === 'local' ) {
            return (
                <div
                    key   = {'stream-canvas'}
                    id    = {'main-div'}
                    style = {{
                        backgroundColor: '#18181b', // Dark background for the VM placeholder
                        visibility      : this.state.streamReady ? 'visible' : 'hidden',
                        outline: 'none',
                        ...this.props.style
                    }}
                >
                    <div
                        id={'aspect-ratio-div'}
                        tabIndex={0}
                        style={{
                            position: 'relative',
                            top: 0,
                            bottom: 0,
                            left: 0,
                            right: 0,
                            paddingBottom: '56.25%',
                            outline: 'none',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: '#52525b'
                        }}
                    >
                        {/* --- BYPASSED FOR VM TESTING --- */}
                        {/* We replaced the <video> element with a visual placeholder text */}
                        <h2 style={{position: 'absolute', top: '50%', transform: 'translateY(-50%)', fontWeight: 'bold', letterSpacing: '0.1em'}}>
                            [ NVIDIA OMNIVERSE STREAM BYPASSED FOR VM TESTING ]
                        </h2>
                        {/* -------------------------------- */}

                        <audio id="remote-audio" muted></audio>
                        <h3 style={{visibility: 'hidden'}} id="message-display">...</h3>
                    </div>
                </div>
            );
        }

        return null;
    }
}

AppStream.propTypes = {
    streamConfig : PropTypes.object.isRequired,
    onLoggedIn   : PropTypes.func.isRequired,
    onStarted    : PropTypes.func.isRequired,
    style        : PropTypes.shape({
        top      : PropTypes.oneOfType([PropTypes.number, PropTypes.string]).isRequired,
        left     : PropTypes.oneOfType([PropTypes.number, PropTypes.string]).isRequired,
        height   : PropTypes.oneOfType([PropTypes.number, PropTypes.string]).isRequired,
        width    : PropTypes.oneOfType([PropTypes.number, PropTypes.string]).isRequired
    }).isRequired
}

AppStream.defaultProps = {
}