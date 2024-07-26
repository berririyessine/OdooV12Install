odoo.define('stock_3dview.3DViewController', function (require) {
    "use strict";

    var ajax = require('web.ajax');
    var core = require('web.core');
    var AbstractController = require('web.AbstractController');

    var ThreeDController = AbstractController.extend({});

    var ThreeDViewController = ThreeDController.extend({

        init: function (parent, context) {
            scope = this;
            this.context = context;
            this._super.apply(this, arguments);
        },

    return ThreeDViewController;
    });

