<?php
class Home extends TPage
{

	public function clickCell($sender, $param)
	{
		$sender->Text = 'Clicked cell #' . $param->SelectedCellIndex;
		$this->lblResult->Text = 'You clicked on cell #'.$param->SelectedCellIndex.' with id='.$sender->ID;
		$sender->render($param->NewWriter);
	}

	public function clickRow($sender, $param)
	{
		$sender->BackColor="yellow";
		$this->lblResult->Text = 'You clicked on row #'.$param->SelectedRowIndex.' with id='.$sender->ID;
		$sender->render($param->NewWriter);
	}
}

