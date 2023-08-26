mergeInto(LibraryManager.library, {
  PrintToConsole: function(str) {
    console.log(UTF8ToString(str));
  }
});
