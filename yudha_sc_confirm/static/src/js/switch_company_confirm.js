/*
     Author => Albertus Restiyanto Pramayudha
     email  => xabre0010@gmail.com
     linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
     youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
*/
odoo.define('yudha_sc_confirm.sc_confirm', function (require) {
'use strict';

    var core = require('web.core');
    var SwitchCompanyMenu = require('web.SwitchCompanyMenu');
    var session = require('web.session');
    var Dialog = require('web.Dialog');
    var _t = core._t;
    require('yudha_yes_no_dialog.yes_no_dialog');

    SwitchCompanyMenu.include({
        events: _.extend({}, SwitchCompanyMenu.prototype.events, {
            'click .dropdown-item[data-menu] div.log_into': '_onConfirmSwitch',
            'keydown .dropdown-item[data-menu] div.log_into': '_onConfirmSwitch',
            'click .dropdown-item[data-menu] div.toggle_company': '_onTogleConfirmSwitch',
            'keydown .dropdown-item[data-menu] div.toggle_company': '_onTogleConfirmSwitch',
        }),
        _onConfirmSwitch: function (ev) {
            var self = this;
            Dialog.yesno(this, _t("Are you sure that you want to Switch To This Company?"), {
                yes_callback: () =>  self._onSwitchCompanyClick(ev),
            });
        },
        _onTogleConfirmSwitch: function (ev) {
            var self = this;
            Dialog.yesno(this, _t("Are you sure that you want to Switch To This Company?"), {
                yes_callback: () => self._onSwitchCompanyClick(ev) ,
            });
        },
        _onSwitchCompanyClick: function (ev) {
            if (ev.type == 'keydown' && ev.which != $.ui.keyCode.ENTER && ev.which != $.ui.keyCode.SPACE) {
                return;
            }
            ev.preventDefault();
            ev.stopPropagation();
            var dropdownItem = $(ev.currentTarget).parent();
            var dropdownMenu = dropdownItem.parent();
            var companyID = dropdownItem.data('company-id');
            var allowed_company_ids = this.allowed_company_ids;
            if (dropdownItem.find('.fa-square-o').length) {
                // 1 enabled company: Stay in single company mode
                if (this.allowed_company_ids.length === 1) {
                    if (this.isMobile) {
                        dropdownMenu = dropdownMenu.parent();
                    }
                    dropdownMenu.find('.fa-check-square').removeClass('fa-check-square').addClass('fa-square-o');
                    dropdownItem.find('.fa-square-o').removeClass('fa-square-o').addClass('fa-check-square');
                    allowed_company_ids = [companyID];
                } else { // Multi company mode
                    allowed_company_ids.push(companyID);
                    dropdownItem.find('.fa-square-o').removeClass('fa-square-o').addClass('fa-check-square');
                }
            }
            $(ev.currentTarget).attr('aria-pressed', 'true');
            $(ev.currentTarget).attr('aria-checked', 'false');
            session.setCompanies(companyID, allowed_company_ids);
        },
    });
});