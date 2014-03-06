package edu.colorado.csdms.wmt.client.ui;

import com.google.gwt.dom.client.Style.Cursor;
import com.google.gwt.dom.client.Style.Unit;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Grid;
import com.google.gwt.user.client.ui.HTML;

/**
 * Supplies a Grid with links for viewing or downloading the input
 * configuration files generated by the parameters set for a component in a
 * model.
 * 
 * @author Mark Piper (mark.piper@colorado.edu)
 */
public class ViewInputFilesPanel extends Grid {

  private String componentId;
  private String urlHTML;
  
  /**
   * Creates a new ViewInputFilesPanel with links built for the current state 
   * of a model component parameter.
   * 
   * @param componentId the id of the model component, a String
   */
  public ViewInputFilesPanel(String componentId) {

    super(1, 6);
    this.componentId = componentId;
    this.getElement().getStyle().setMarginTop(2, Unit.EM);
    this.setCellPadding(5); // px

    // TODO Should use DataURL.
    urlHTML =
        "http://csdms.colorado.edu/wmt/components/format/" + this.componentId
            + "?defaults=True";
    HTML viewHTML = new HTML("<a href='" + urlHTML + "'>HTML</a>");
    HTML viewText = new HTML("text"); // TODO Add link.
    HTML viewJSON = new HTML("JSON"); // TODO Add link.

    viewHTML.getElement().getStyle().setCursor(Cursor.POINTER);
    viewText.getElement().getStyle().setCursor(Cursor.POINTER);
    viewJSON.getElement().getStyle().setCursor(Cursor.POINTER);

    this.setWidget(0, 0, new HTML("View input files:"));
    this.setWidget(0, 1, viewHTML);
    this.setWidget(0, 2, new HTML("|"));
    this.setWidget(0, 3, viewText);
    this.setWidget(0, 4, new HTML("|"));
    this.setWidget(0, 5, viewJSON);

    /*
     * Intercepts the click on the link in the viewHTML cell and directs it
     * to open in another tab/window.
     */
    viewHTML.addClickHandler(new ClickHandler() {
      @Override
      public void onClick(ClickEvent event) {
        event.preventDefault();
        Window.open(urlHTML, "viewInputFiles", null);
      }
    });
  }

}
