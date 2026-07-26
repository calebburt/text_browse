LISTENERS = {}

function Node(handle) {
    this.handle = handle;
}

Node.prototype.querySelectorAll = function(selector) {
    var handles = call_python("querySelectorAll", this.handle + " " + selector);
    return handles.map(function(h) {
        return new Node(h);
    });
};
Node.prototype.querySelector = function(selector) {
    var nodes = this.querySelectorAll(selector);
    return nodes.length ? nodes[0] : null;
};
Node.prototype.getAttribute = function(attr) {
    return call_python("getAttribute", this.handle, attr);
};
Node.prototype.setAttribute = function(attr, value) {
    return call_python("getAttribute", this.handle, attr, value);
};
Node.prototype.hasAttribute = function(attr) {
    return this.getAttribute(attr) !== null;
};
Node.prototype.getElementsByTagName = function(tag) {
    return this.querySelectorAll(tag);
};
Object.defineProperty(Node.prototype, "id", {
    set: function(a) {
        return this.setAttribute("id", tag);
    },
    get: function() {
        return this.getAttribute("id");
    }
});
Object.defineProperty(Node.prototype, "className", {
    set: function(s) {
        return this.setAttribute("class", tag);
    },
    get: function() {
        return this.getAttribute("class");
    }
});
Object.defineProperty(Node.prototype, "tagName", {
    get: function() {
        return this.getAttribute("tag");
    }
});
Object.defineProperty(Node.prototype, 'innerHTML', {
    set: function(s) {
        call_python("innerHTML_set", this.handle, s.toString());
    },
    get: function() {
        call_python("innerHTML_get", this.handle);
    }
})

/* ---------------------------
   EVENTS
---------------------------- */
function Event(type) {
    this.type = type
    this.do_default = true;
}

Event.prototype.preventDefault = function() {
    this.do_default = false;
}

Node.prototype.addEventListener = function(type, listener) {
    if (!LISTENERS[this.handle]) {
        LISTENERS[this.handle] = {};
    }
    var dict = LISTENERS[this.handle];
    if (!dict[type]) {
        dict[type] = [];
    }
    var list = dict[type];
    list.push(listener);
}
Node.prototype.dispatchEvent = function(evt) {
    var type = evt.type;
    var handle = this.handle;
    var list = (LISTENERS[handle] && LISTENERS[handle][type]) || [];
    for (var i = 0; i < list.length; i++) {
        list[i].call(this, evt);
    }
    return evt.do_default;
}

/* ---------------------------
   BASIC LOGGING
---------------------------- */
console = {
    log: function(args) {
        call_python("log", args);
    }
};

/* ---------------------------
   DOCUMENT QUERYING
---------------------------- */
document = {
    /* Core primitive */
    querySelectorAll: function(selector) {
        var handles = call_python("querySelectorAll", selector);
        return handles.map(function(h) {
            return new Node(h);
        });
    },

    /* Derived from querySelectorAll */
    querySelector: function(selector) {
        var nodes = document.querySelectorAll(selector);
        return nodes.length ? nodes[0] : null;
    },

    /* Derived from querySelectorAll */
    getElementById: function(id) {
        var nodes = document.querySelectorAll("#" + id);
        return nodes.length ? nodes[0] : null;
    },

    /* Derived from querySelectorAll */
    getElementsByTagName: function(tag) {
        return document.querySelectorAll(tag);
    }
};
