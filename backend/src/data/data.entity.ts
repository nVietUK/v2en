import { ObjectType } from '@nestjs/graphql';
import { Md5 } from 'ts-md5';
import { Column, Entity, PrimaryColumn, PrimaryGeneratedColumn } from 'typeorm';
import { IsDataExistedByHashValue } from './data.validator';

@Entity()
@ObjectType('DataObject')
export class Data {
	constructor(
		origin = '',
		translated = '',
		translator = '',
		verified = false,
	) {
		this.origin = origin;
		this.translated = translated;
		this.translator = translator;
		this.verified = verified;
	}

	@PrimaryGeneratedColumn()
	@PrimaryColumn('int')
	id?: number;

	@Column('longtext')
	origin: string;

	@Column('longtext')
	translated: string;

	@Column('longtext')
	translator: string;

	@Column('longtext', { nullable: false })
	@IsDataExistedByHashValue({ message: 'hashValue is existed' })
	get hashValue(): string {
		return Md5.hashStr(
			`${this.origin} ${this.translated} ${this.translator}`,
		).toString();
	}
	set hashValue(value: string) {
		value;
	}

	@Column({ default: false })
	verified: boolean;
}
