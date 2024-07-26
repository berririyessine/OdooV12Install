odoo.define('stock_3dview.3DView', function (require) {
    "use strict";

    var ajax = require('web.ajax');
    var core = require('web.core');
    var AbstractController = require('web.AbstractController');
    var AbstractController1 = AbstractController.extend({});
    var AbstractModel = require('stock_3dview.3DViewModel');
    var AbstractRenderer = require('stock_3dview.3DViewRenderer');
    var AbstractView = require('web.AbstractView');
    var data_manager = require('web.data_manager');
    var session = require('web.session');
    var view_registry = require('web.view_registry');
    var _lt = core._lt;
    var QWeb = core.qweb;

    var refSys;
    var scale;
    var container, stats;
    var camera, controls, scene, renderer;
    var target;
    var cross;
    var gui;
    var cameraSettings = {};
    var cs = 1; // with GUI;
    var objects = [];
    var raycaster;
    var mouse;
    var domain = [];

    var scope;

    if ( ! Detector.webgl ) Detector.addGetWebGLMessage();

    var ThreeDView = AbstractView.extend({
        config: {
            Model: AbstractModel,
            Controller: AbstractController1,
            Renderer: AbstractRenderer,
        },
        display_name: _lt('ThreeD View'),
        icon: 'fa-cubes',
        template: '3DView',
        view_type: 'threedview',

        init: function (parent, context) {
            scope = this;
            this.context = context;
            this._super.apply(this, arguments);
            return this;
        },

    });

    view_registry.add('threedview', ThreeDView);

        return ThreeDView;
    });

