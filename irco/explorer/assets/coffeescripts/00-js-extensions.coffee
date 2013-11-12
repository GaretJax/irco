if typeof String.prototype.startswith != 'function'
    String.prototype.startswith = (str) ->
        return this.slice(0, str.length) == str
