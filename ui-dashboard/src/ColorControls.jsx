/**
 * @file      : ColorControls.jsx
 * @summary   :
 * @author    : Charles Best <cbest@nvidia.com>
 * @created   : 2023-12-13
 * @copywrite : 2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
 * @exports   : ColorControls
 */

import React from "react";
import PropTypes from 'prop-types';
import { Button } from "react-bootstrap";

export default class ColorControls extends React.Component {
    render() {
        const buttons = this.props.options.map((option, idx) => {
            return (
                <Button
                    key     = {idx}
                    onClick = {() => this.props.onSelect(option.value)}
                    style   = {{
                        zIndex          : 1000,
                        width           : 170,
                        minHeight       : 60,
                        borderRadius    : 0,
                        marginTop       : 10,
                        outline         : 'none',
                        backgroundColor : option.value === this.props.selected ? '#bbbbbb' : '#ededed',
                        color           : '#656565',
                        borderColor     : '#656565',
                        borderWidth     : 1,
                        marginLeft      : 30,
                    }}
                >
                    {option.label}
                </Button>
            );
        });

        return (
            <div
                style = {{
                    position        : 'absolute',
                    top             : 0,
                    right           : 0,
                    width           : this.props.width,
                    height          : '100%',
                    backgroundColor : '#FEFEFE',
                    color           : '#656565',
                    textAlign       : 'left'
                }}
            >
                <div
                    style = {{
                        marginLeft : 30,
                        marginTop  : 30,
                        fontSize   : 25
                    }}>
                        {'Leather'}
                    </div>
                {buttons}
            </div>
        );
    }
}

ColorControls.propTypes = {
    width    : PropTypes.number.isRequired,
    options  : PropTypes.arrayOf(PropTypes.object).isRequired,
    selected : PropTypes.string,
    onSelect : PropTypes.func,
}

ColorControls.defaultProps = {
    selected : ''
}
