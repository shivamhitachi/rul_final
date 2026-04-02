/**
 * @file      : BackgroundControls.jsx
 * @summary   :
 * @author    : Charles Best <cbest@nvidia.com>
 * @created   : 2023-12-13
 * @copywrite : 2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
 * @exports   : BackgroundControls
 */

import React from "react";
import PropTypes from 'prop-types';
import { Button } from "react-bootstrap";

export default class BackgroundControls extends React.Component {
    render() {
        const buttons = this.props.options.map((option, idx) => {
            return (
                <div
                    key     = {idx}
                >
                <Button
                    onClick = {() => this.props.onSelect(option.value)}
                    style   = {{
                        width           : 170,
                        minHeight       : 60,
                        borderRadius    : 0,
                        margin          : 10,
                        outline         : 'none',
                        backgroundColor : option.value === this.props.selected ? '#bbbbbb' : '#ededed',
                        color           : '#656565',
                        borderColor     : '#656565',
                        borderWidth     : 1,
                        zIndex          : 500
                    }}
                >
                    {option.label}
                </Button>
                </div>
            );
        });

        return (
            <div
                style = {{
                    position        : 'absolute',
                    bottom          : 0,
                    left            : 0,
                    width           : this.props.width,
                    height          : 100,
                    backgroundColor : '#00000000',
                    textAlign       : 'left',
                    marginLeft      : 30,
                    display         : 'flex',
                    alignItems      : 'stretch',
                    zIndex          : 500
                }}
            >
                {buttons}
            </div>
        );
    }
}

BackgroundControls.propTypes = {
    width    : PropTypes.oneOfType([PropTypes.number, PropTypes.string]).isRequired,
    options  : PropTypes.arrayOf(PropTypes.object).isRequired,
    selected : PropTypes.string,
    onSelect : PropTypes.func
}

BackgroundControls.defaultProps = {
    selected : ''
}
