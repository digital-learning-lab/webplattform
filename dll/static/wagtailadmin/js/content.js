(function () {
  'use strict';
  const React = window.React;
  const Modifier = window.DraftJS.Modifier;
  const EditorState = window.DraftJS.EditorState;
  const ModalWorkflow = window.draftail.ModalWorkflowSource;

  const DEMO_STOCKS = ['AMD', 'AAPL', 'TWTR', 'TSLA', 'BTC'];

// Not a real React component – just creates the entities as soon as it is rendered.
  class ContentSource extends React.Component {
    componentDidMount() {
      const { editorState, entityType, onComplete } = this.props;

      const content = editorState.getCurrentContent();
      const selection = editorState.getSelection();

      const contentId = 20;

      // Uses the Draft.js API to create a new entity with the right data.
      const contentWithEntity = content.createEntity(entityType.type, 'IMMUTABLE', {
        content: contentId,
      });
      const entityKey = contentWithEntity.getLastCreatedEntityKey();

      // We also add some text for the entity to be activated on.
      const text = `Some nice title`;

      const newContent = Modifier.replaceText(content, selection, text, null, entityKey);
      const nextState = EditorState.push(editorState, newContent, 'insert-characters');

      onComplete(nextState);
    }

    render() {
      return null;
    }
  }

  const Content = (props) => {
    const { entityKey, contentState } = props;
    const data = contentState.getEntity(entityKey).getData();
    console.log(props);
    return React.createElement('a', {
      role: 'button',
      'data-content': props,
      onMouseUp: () => {
        window.open(data.url);
      },
    }, props.children);
  };

  window.draftail.registerPlugin({
    type: 'CONTENT',
    source: ContentSource,
    decorator: Content,
  });

})();