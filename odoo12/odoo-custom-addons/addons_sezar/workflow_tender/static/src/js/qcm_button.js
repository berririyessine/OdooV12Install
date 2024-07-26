odoo.define('custom_project.web_export_view', function (require) {
"use strict";
var core = require('web.core');
var ListView = require('web.ListView');
var ListController = require("web.ListController");

var includeDict = {
    renderButtons: function () {
        this._super.apply(this, arguments);
         if (this.modelName === "offre.physique") {
            var your_btn = this.$buttons.find('button.o_button_help');

            your_btn.on('click', this.proxy('o_button_help'));
}
if (this.modelName === "offre.tuneps") {
            var your_btn = this.$buttons.find('button.o_button_help_tuneps');

            your_btn.on('click', this.proxy('o_button_help'));
}

    },
    o_button_help: function(){
    if (this.modelName === "offre.physique") {

      this.do_action('workflow_tender.action_qcm_physique');
      }
    if (this.modelName === "offre.tuneps") {

    this.do_action('workflow_tender.action_qcm_tuneps');
    }
    }

};
ListController.include(includeDict);
});