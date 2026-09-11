<?php

class Home extends TPage
{
	public function readValue($sender, $param)
	{
		$this->Result->Text = 'The hidden field holds "' . $this->Hidden1->Value . '".';
	}

	public function writeValue($sender, $param)
	{
		$this->Hidden1->Value = 'written by the server at ' . date('H:i:s');
		$this->Result->Text = 'The hidden field now holds "' . $this->Hidden1->Value . '".';
	}

	public function valueChanged($sender, $param)
	{
		$this->ChangeLog->Text = 'OnValueChanged fired. The new value is "' . $sender->Value . '".';
	}
}
