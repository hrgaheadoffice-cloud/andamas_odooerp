/*
     Author => Albertus Restiyanto Pramayudha
     email  => xabre0010@gmail.com
     linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
     youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
*/
odoo.define('yudha_yes_no_dialog.yes_no_dialog', function (require) {
'use strict';

    var core = require('web.core');
    var dom = require('web.dom');
    var Widget = require('web.Widget');
    var Dialog = require('web.Dialog');
    var _t = core._t;
    const OwlDialog = require('web.OwlDialog');
    Dialog.yesno = function (owner, message, options) {
        /**
         * Creates an improved callback from the given callback value at the given
         * key from the parent function's options parameter. This is improved to:
         *
         * - Prevent calling given callbacks once one has been called.
         *
         * - Re-allow calling callbacks once a previous callback call's returned
         *   Promise is rejected.
         */
        let isBlocked = false;
        function makeCallback(key) {
            const callback = options && options[key];
            return function () {
                if (isBlocked) {
                    // Do not (re)call any callback and return a rejected Promise
                    // to prevent closing the Dialog.
                    return Promise.reject();
                }
                isBlocked = true;
                const callbackRes = callback && callback.apply(this, arguments);
                Promise.resolve(callbackRes).guardedCatch(() => {
                    isBlocked = false;
                });
                return callbackRes;
            };
        }
        var buttons = [
            {
                text: _t("Yes"),
                classes: 'btn-primary',
                close: true,
                click: makeCallback('yes_callback'),
            },
            {
                text: _t("No"),
                close: true,
                click: makeCallback('no_callback'),
            }
        ];
        return new Dialog(owner, _.extend({
            size: 'medium',
            buttons: buttons,
            $content: $('<main/>', {
                role: 'alert',
                text: message,
            }),
            title: _t("Confirmation"),
            onForceClose: options && (options.onForceClose || options.cancel_callback),
        }, options)).open({shouldFocusButtons:true});
    };
});