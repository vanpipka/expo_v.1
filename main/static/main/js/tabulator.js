$(document).ready(function() {
    var table;
    var url = 'http://127.0.0.1:56503/adminexpo/workers/';
    $.get(url, function(response) {

      var dateEditor = function(cell, onRendered, success, cancel){
          //cell - the cell component for the editable cell
          //onRendered - function to call when the editor has been rendered
          //success - function to call to pass the successfuly updated value to Tabulator
          //cancel - function to call to abort the edit and return to a normal cell

          //create and style input
          var cellValue = cell.getValue(),
          input = document.createElement("input");

          input.setAttribute("type", "checkbox");

          input.value = cellValue;

          onRendered(function(){
              input.focus();
              input.style.height = "100%";
          });

          function onChange(){
              console.log(input.checked);
              if(input.checked != cellValue){
                  success(input.checked);
              }else{
                  cancel();
              }
          }

          //submit new value on blur or change
          input.addEventListener("blur", onChange);

          //submit new value on enter
          input.addEventListener("keydown", function(e){
              if(e.keyCode == 13){
                  onChange();
              }

              if(e.keyCode == 27){
                  cancel();
              }
          });

          return input;
      };
      //custom max min header filter
    var minMaxFilterEditor = function(cell, onRendered, success, cancel, editorParams){

      var end;

      var container = document.createElement("span");

      //create and style inputs
      var start = document.createElement("input");
      start.setAttribute("type", "number");
      start.setAttribute("placeholder", "Min");
      start.setAttribute("min", 0);
      start.setAttribute("max", 100);
      start.style.padding = "4px";
      start.style.width = "50%";
      start.style.boxSizing = "border-box";

      start.value = cell.getValue();

      function buildValues(){
          success({
              start:start.value,
              end:end.value,
          });
      }

      function keypress(e){
          if(e.keyCode == 13){
              buildValues();
          }

          if(e.keyCode == 27){
              cancel();
          }
      }

      end = start.cloneNode();
      end.setAttribute("placeholder", "Max");

      start.addEventListener("change", buildValues);
      start.addEventListener("blur", buildValues);
      start.addEventListener("keydown", keypress);

      end.addEventListener("change", buildValues);
      end.addEventListener("blur", buildValues);
      end.addEventListener("keydown", keypress);


      container.appendChild(start);
      container.appendChild(end);

      return container;
    }

    //custom max min filter function
    function minMaxFilterFunction(headerValue, rowValue, rowData, filterParams){
      //headerValue - the value of the header filter element
      //rowValue - the value of the column in this row
      //rowData - the data for the row being filtered
      //filterParams - params object passed to the headerFilterFuncParams property

          if(rowValue){
              if(headerValue.start != ""){
                  if(headerValue.end != ""){
                      return rowValue >= headerValue.start && rowValue <= headerValue.end;
                  }else{
                      return rowValue >= headerValue.start;
                  }
              }else{
                  if(headerValue.end != ""){
                      return rowValue <= headerValue.end;
                  }
              }
          }

      return false; //must return a boolean, true if it passes the filter.
    }

        table = new Tabulator('#example-table', {
            data: response.dataset.dataset,
            layout: 'fitColumns',
            pagination: 'local',
            paginationSize: 8,
            initialSort: [
                { column: 'age', dir: 'desc' }
            ],
            columns: [
                { title: 'id', field: 'id', visible: false },
                {
                    title: 'Специалист',
                    headerFilter: "input",
                    field: 'name',
                    width: 550,
                    formatter: function(cell) {
                        var data = cell.getData();
                        return '<img style="height: 25px" src="'+ data.resizefotourl +'" /><a href="' + data.url + '" target="_blank">' + data.name + '</a>';
                    }
                },
                {
                    title: 'Город',
                    field: 'city',
                    align: 'left',
                    formatter: function(cell) {
                          var data = cell.getData();
                          return data.city.name;
                    }
                },
                {
                    title: 'Был онлайн',
                    field: 'lastonline',
                    align: 'left',
                    tooltip: true,
                    formatter: function(cell) {
                      var data = cell.getData();

                      var options = {
                          year: '2-digit',
                          month: '2-digit',
                          day: '2-digit',
                          hour: '2-digit',
                          minute: '2-digit',
                      };

                      var date = data.lastonline.toLocaleString("ru", options) ;
                      return date.substr(0, 10);
                  }
                },
                { title: 'Возраст', field: 'age' },
                {
                    title: 'Заблокирован',
                    field: 'block',
                    editor: dateEditor,
                    formatter: function(cell) {
                      var data = cell.getData();
                      if (data.block == true) {
                          return '<input type="checkbox" checked>';
                      }else{
                          return '<input type="checkbox">';
                      }

                    }
                },
                {
                    title: 'Проверен',
                    field: 'datacheck',
                    editor: dateEditor,
                    formatter: function(cell) {
                      var data = cell.getData();
                      if (data.datacheck == true) {
                          return '<input type="checkbox" checked>';
                      }else{
                          return '<input type="checkbox">';
                      }

                    }
                },
                {
                    title: '',
                    formatter: function(cell) {
                        return 'Сохранить';

                    },
                    cellClick:function(e, cell){save_tr(cell.getData());}

                }



            ]
        });

    });

});
